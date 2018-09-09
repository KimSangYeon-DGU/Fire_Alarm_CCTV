import socket as sock
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import math
import struct
import numpy as np

def send_msg(sock, msg):
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

cam_width = 640
cam_height = 480

camera = PiCamera()
camera.resolution = (cam_width, cam_height)
#camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(cam_width, cam_height))
rawCapture.truncate(0)

ip = "192.168.219.195"
port = 9999
addr = (ip, port)

client = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
client.connect(addr)
#client.settimeout(1.0)
#client.sendto("Hello World".encode(), addr)#("Hello World", addr)
BUFF_SIZE = 4096
for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):    
    frame = frame1.array
    #print(len(bytes(frame)))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode(".jpg", frame, encode_param)
    bytes_len = len(imgencode)
    print(bytes_len)
    data = np.array(imgencode)
    stringData = data.tostring()

    client.send(str(len(stringData)).ljust(16).encode("utf-8"))
    client.send(stringData)

    rawCapture.truncate(0)
    
client.close()
camera.close()

