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
'''
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
type: function
name: init
description: initialize required constants variables
'''
def init():
    global addr, img_file_path, android_connection
    print("init")

    ip = sock.gethostname()
    port = 9999
    addr = (ip, port)

    root_folder = os.path.dirname(os.path.abspath(__file__)) # Get root directory path
    img_file_path = os.path.join(root_folder, 'test.jpg')

    android_connection = False

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
    global addr, android_connection, conn_android
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read() 
        if ret == False:
            break

        if android_connection:
            width, height = frame.shape[:2]
            frame = cv2.resize(frame, (int(height/4), int(width/4)))
            encoded = convert_to_base64(frame)
            outjson = {}
            outjson['img'] = encoded
            outjson['leaf'] = "leaf"
            json_data = json.dumps(outjson)
            write_utf8(str(json_data), conn_android)
            android_connection = False
        
'''
type: function
name: wait_cctv
description: wait android connection
'''
def wait_android():
    global addr, img_file_path, android_connection, conn_android

    while True:
        print("Wating android...")

        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # initialize server socket
        server.bind((sock.gethostname(), 8888)) # socket bind

        print('listen to android connection')
        server.listen(1) # listen and wait for one client

        conn_android, addr = server.accept() # accept

        while True:
            buff = conn_android.recv(1024)
            buff = buff.decode("utf-8")
            print(buff)
            if buff == "Conn":
                android_connection = True
                print("Android Connected")

            elif buff == "Exit":
                android_connection = False
                server.close()
                print("Android Exited")
                break

if __name__ == "__main__":
    init()
    t = threading.Thread(target=wait_android)
    t.start()
    run_webcam()
    t.join()
    
