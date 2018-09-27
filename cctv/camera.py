import socket as sock
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import math
import json
import numpy as np
import struct

def send_msg(sock, msg):
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)
    
def write_utf8(msg, socket):
    encoded = msg.encode(encoding='utf-8')
    socket.sendall(struct.pack('>i', len(encoded)))
    socket.sendall(encoded)

def init():
    global cam_width, cam_height, ip, port, BUFF_SIZE
    cam_width = 1920
    cam_height = 1080
    #cam_width = 1280
    #cam_height = 720
    ip = "192.168.219.166"
    port = 9000
    BUFF_SIZE = 4096

def run_cctv():
    global cam_width, cam_height, ip, port, BUFF_SIZE
    
    camera = PiCamera()
    camera.resolution = (cam_width, cam_height)
    #camera.framerate = 60
    rawCapture = PiRGBArray(camera, size=(cam_width, cam_height))
    rawCapture.truncate(0)

    client = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    client.connect((ip, port))
    
    for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):    
        frame = frame1.array
        #print(len(bytes(frame)))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        
        result, imgencode = cv2.imencode(".jpg", frame, encode_param)
        bytes_len = len(imgencode)
        #print(bytes_len)
        data = np.array(imgencode)
        stringData = data.tostring()
        client.send(str(len(stringData)).ljust(16).encode("utf-8"))
        client.send(stringData)
        
        rawCapture.truncate(0)
        
    client.close()
    camera.close()
if __name__ == "__main__":
    init()
    run_cctv()
