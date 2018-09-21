'''
this is a demo server app
'''
import os, cv2
import socket as sock
from io import BytesIO
from firebase import firebase
from pyfcm import FCMNotification
import base64
import numpy as np
import threading
import struct
import pickle
import json
import datetime

def write_utf8(msg, socket):
    encoded = msg.encode(encoding='utf-8')
    socket.sendall(struct.pack('>i', len(encoded)))
    socket.sendall(encoded)

'''
type: function
name: recvall
description: receive all packets by spliting total stream to 4096
the dtype modes are string and bytes, the bytes mode is to read image byte array
and the string mode is to read the length of total packets

def recvall(sock, count, dtype):

    if dtype == "bytes":
        buf = b''
    else:
        buf = ''
    while count:
        newbuf = sock.recv(count)
        if dtype == "string":
            newbuf = newbuf.decode("utf-8")
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf
'''

def recvall(sock, size):
    received_chunks = []
    buf_size = 4096
    remaining = size
    while remaining > 0:
        received = sock.recv(min(remaining, buf_size))
        if not received:
            raise Exception('unexcepted EOF')
        received_chunks.append(received)
        remaining -= len(received)
    return b''.join(received_chunks)

def read_utf8(sock):
    len_bytes = recvall(sock, 4)
    length = struct.unpack('>i', len_bytes)[0]
    encoded = recvall(sock, length)
    return str(encoded, encoding='utf-8')

'''
type: function
name: init
description: initialize required constants variables
'''
def init():
    global addr, img_file_path, android_connection, HD, display_width, display_height, REC, fourcc, rec_dir, DB_addr, cur_dir
    print("init")

    ip = sock.gethostname()
    port = 9999
    addr = (ip, port)

    root_folder = os.path.dirname(os.path.abspath(__file__)) # Get root directory path
    img_file_path = os.path.join(root_folder, 'test.jpg')

    android_connection = False

    HD = "off"
    display_width = None
    display_height = None
    REC = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    cur_dir = os.getcwd()
    rec_dir = os.path.join(cur_dir, "record")

    DB_addr = "Database address"
    PUSH_addr = "PUSH address"

def convert_to_base64(image):
    img_str = cv2.imencode('.png', image)[1].tostring()
    b64 = base64.b64encode(img_str)
    return b64.decode('utf-8')


def set_video_writer(video_name, fourcc, FPS, width, height):
    global video

    video = cv2.VideoWriter(video_name, fourcc, FPS, (width, height))

'''
type: function
name: run_webcam
description: wait raspberry pi connection
'''
def run_webcam():
    global addr, android_connection, conn_android, HD, display_width, display_height, video, REC, fourcc, rec_dir, cur_dir

    cap = cv2.VideoCapture(0)
    pre_date = ""

    ENCODE = True
    while True:
        ret, frame = cap.read() 
        if ret == False:
            break

        if REC:
            cur_date = datetime.datetime.date(datetime.datetime.now())
            if pre_date != cur_date:
                file_names = os.listdir(rec_dir)
                file_names.sort()
                num_of_files = len(file_names)
                if num_of_files > 3:
                    os.remove(os.path.join(rec_dir, file_names[0]))
                set_video_writer(os.path.join(rec_dir, str(cur_date)+".avi"), fourcc, 30, width=640, height=480)
            pre_date = cur_date
            video.write(frame)

        if android_connection:
            height, width = frame.shape[:2] # 480, 640
            print(width, height)

            if HD == "on": 
                rsz_frame = cv2.resize(frame, (int(display_height/2), int(display_width/2)))
            else:
                rsz_frame = cv2.resize(frame, (int(display_height/6), int(display_width/6)))

            encoded = convert_to_base64(rsz_frame)
            
            outjson = {}
            outjson['img'] = encoded
            outjson['state'] = "Normal"
            json_data = json.dumps(outjson)
            write_utf8(str(json_data), conn_android)
            android_connection = False

    cap.release()
    video.release()
        

def send_fire_image(cam, date):
    global display_width, display_height

    fire_dir = os.path.join(cur_dir, "fire")
    cam_dir = os.path.join(fire_dir, cam)
    frame = cv2.imread(os.path.join(cam_dir, date+".png"))
    rsz_frame = cv2.resize(frame, (int(display_width/4), int(display_height/4)))
    encoded = convert_to_base64(rsz_frame)
    outjson = {}
    outjson['encoded'] = encoded
    outjson['state'] = "Fire"
    json_data = json.dumps(outjson)
    write_utf8(str(json_data), conn_android)

def send_info_from_firebase(cam, title):
    global conn_android, DB_addr

    print(cam)
    fb = firebase.FirebaseApplication(DB_addr, None)
    user_name = "user1"
    outjson = fb.get("/users/"+user_name+"/"+str(cam)+"/"+str(title), None)
    print(outjson)
    write_utf8(str(outjson), conn_android)

'''
type: function
name: wait_cctv
description: wait android connection
'''
def wait_android():
    global addr, img_file_path, android_connection, conn_android, HD, display_width, display_height

    while True:
        print("Wating android...")

        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # initialize server socket
        server.bind((sock.gethostname(), 8888)) # socket bind

        print('listen to android connection')
        server.listen(1) # listen and wait for one client

        conn_android, addr = server.accept() # accept

        while True:
            try:
                msg = read_utf8(conn_android)
            except ConnectionResetError:
                print("The connection was forcefully disconnected.")
                server.close()
                break
            except Exception:
                print("The connection was forcefully disconnected.")
                server.close()
                break

            msg = json.loads(msg)
            status = msg["status"]
            print(status)
            if status == "conn":
                HD = msg["hd"]
                display_width = msg["width"]
                display_height = msg["height"]
                android_connection = True
                #print("Android Connected")

            elif status == "exit":
                android_connection = False
                server.close()
                #print("Android Exited")
                break

            elif status == "info":
                send_info_from_firebase(msg["camera"], status)
                break
            elif status == "log":
                send_info_from_firebase(msg["camera"], status)
                break
            elif status == "fire":
                display_width = msg["width"]
                display_height = msg["height"]
                send_fire_image(msg["camera"], msg["date"])
                break

if __name__ == "__main__":
    init()
    t = threading.Thread(target=wait_android)
    t.start()
    run_webcam()
    t.join()