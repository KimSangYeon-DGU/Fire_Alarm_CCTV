############# CCTV ##############
#
# Author: Alex Kim
# Date: 9/28/18
# Description: 
# This is the Raspberry Pi CCTV code.

# Import packages
import socket as sock
import cv2
from time import sleep
import math
import json
import numpy as np
import struct
import queue
import threading
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

'''
Type: function
Name: send_frame
Description: 
The function to send frames to the server. 
JPEG encoding is used to facilitate communication before sending frames uisng OpenCV.
'''
def send_frame(sock):
    global encode_param, frame_queue

    while True:
        try:
            # Verify that the queue has frame to be processed
            if frame_queue.empty() == True:
                continue

            # Get first frame in queue    
            frmae  = frame_queue.get()

            # Encoding to facilitate communication
            _, encoded_img = cv2.imencode(".jpg", frame, encode_param)

            # Convert encoded image into a numpy array format
            np_arr_img = np.array(encoded_img)

            # Convert numpy array to string for sending with TCP socket
            str_img = np_arr_img.tostring()

            # Send string img length first for loop on the server side
            sock.send(str(len(str_img)).ljust(16).encode("utf-8"))

            # Send string image
            sock.send(str_img)
        except IOError:
            print("Send Error")
            return

'''
Type: function
Name: init
Description: 
Initialize necessary variables and constants before running cctv.
'''
def init():
    global cam_width, cam_height, IP, PORT, encode_param, raw_capture, camera, frame_queue, QUEUE_SIZE, TIMEOUT
    cam_width = 1920
    cam_height = 1080
    IP = "192.168.219.166"
    PORT = 9000
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    camera = PiCamera()
    camera.resolution = (cam_width, cam_height)
    raw_capture = PiRGBArray(camera, size=(cam_width, cam_height))

    frame_queue = queue.Queue()
    QUEUE_SIZE = 60
    TIMEOUT = 5

def connect_to_server():
    global IP, PORT, TIMEOUT
    conn = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    conn.settimeout(TIMEOUT)

    try:
        conn.connect((IP, PORT))
        send_frame(conn)
    except sock.timeout:
        print("Connection time out")
        conn.close()
        time.sleep(120)
        connect_to_server()

'''
Type: function
Name: init
Description: 
Initialize necessary variables and constants before running cctv.
'''
def get_frame():
    global raw_capture, camera, frame_queue, QUEUE_SIZE

    raw_capture.truncate(0)
    for raw_frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):    
        frame = raw_frame.array
        if frame_queue.qsize() < QUEUE_SIZE:
            frame_queue.put(frame)
        else:
            frame_queue.get()
            frame_queue.put(frame)

        raw_capture.truncate(0)
        
    camera.close()

if __name__ == "__main__":
    init()
    frame_thread = threading.Thread(target=get_frame)
    conn_thread = threading.Thread(target=connect_to_server)
    frame_thread.start()
    conn_thread.start()

    frame_thread.join()
    conn_thread.join()
