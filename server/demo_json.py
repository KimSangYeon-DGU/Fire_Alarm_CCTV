'''
this is a demo server app
'''
import os, cv2
import socket as sock
from PIL import Image
from io import BytesIO
import base64
import numpy as np
import threading
import struct
import pickle
import json

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
    global addr, img_file_path, android_connection, HD, display_width, display_height
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

def convert_to_base64(image):
    img_str = cv2.imencode('.png', image)[1].tostring()
    b64 = base64.b64encode(img_str)
    return b64.decode('utf-8')

'''
type: function
name: run_webcam
description: wait raspberry pi connection
'''
def run_webcam():
    global addr, android_connection, conn_android, HD, display_width, display_height
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read() 
        if ret == False:
            break

        if android_connection:
            #width, height = frame.shape[:2]

            if HD == "on": 
                frame = cv2.resize(frame, (int(display_height/2), int(display_width/2)))
            else:
                frame = cv2.resize(frame, (int(display_height/6), int(display_width/6)))

            encoded = convert_to_base64(frame)
            outjson = {}
            outjson['img'] = encoded
            outjson['state'] = "Normal"
            json_data = json.dumps(outjson)
            write_utf8(str(json_data), conn_android)
            android_connection = False
        
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
            HD = msg["hd"]
            
            display_width = msg["width"]
            display_height = msg["height"]

            if status == "conn":
                android_connection = True
                #print("Android Connected")

            elif status == "exit":
                android_connection = False
                server.close()
                #print("Android Exited")
                break
            

if __name__ == "__main__":
    init()
    t = threading.Thread(target=wait_android)
    t.start()
    run_webcam()
    t.join()
    
