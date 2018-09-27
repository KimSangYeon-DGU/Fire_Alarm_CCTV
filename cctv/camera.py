import socket as sock
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import math
import json
import numpy as np
import struct


'''
Type: function
Name: init
Description: 
Initialize necessary variables and constants before running cctv.
'''
def init():
    global cam_width, cam_height, IP, PORT, encode_param
    cam_width = 1920
    cam_height = 1080
    IP = "192.168.219.166"
    PORT = 9000
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

'''
Type: function
Name: send_frame
Description: 
The function to send frames to the server. 
JPEG encoding is used to facilitate communication before sending frames uisng OpenCV.
'''
def send_frame(sock, frame):
    global encode_param

    try:
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
    except Exception as ex:
        print("Send Error>> ", ex)
        raise IOError


def run_cctv():
    global cam_width, cam_height, IP, PORT
    
    camera = PiCamera()
    camera.resolution = (cam_width, cam_height)
    raw_capture = PiRGBArray(camera, size=(cam_width, cam_height))
    raw_capture.truncate(0)

    try:
        conn = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        conn.connect((IP, PORT))
    except Exception as ex:
        print("Socket Error>> ", ex)
        return None
    
    for raw_frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):    
        frame = raw_frame.array
        try:
            send_frame(conn, frame)
            msg = conn.recv(10)
            if str(msg, "utf-8") != "OK":
                break
        except IOError:
            break
        raw_capture.truncate(0)
        
    conn.close()
    camera.close()
    
if __name__ == "__main__":
    init()
    run_cctv()
