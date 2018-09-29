################# CCTV ##################
#
# Author: Alex Kim
# Date: 9/28/18
# Description: 
# This is the Raspberry Pi CCTV code.

# Import packages
import socket as sock
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

'''
Type: function
Name: init
Description: 
Initialize necessary variables and constants before running cctv.
'''
def init():
    global cam_width, cam_height, IP, PORT, encode_param

    # Camera width and height
    cam_width = 1920
    cam_height = 1080

    # Server's IP to connect 
    IP = "192.168.219.166"

    # Port to connect
    PORT = 9000

    # Encoding parameter
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

'''
Type: function
Name: run_cctv
Description: 
It is actually a function that executes cctv. 
Obtain a frame from the Pi Camera and send it to the server. 
Send and receive message to synchronize with the server when transmitting.
'''
def run_cctv():
    global cam_width, cam_height, IP, PORT
        
    # Set PiCamera
    camera = PiCamera()

    # Set Camera's resolution
    camera.resolution = (cam_width, cam_height)

    # To get a 3-dimensional RGB array
    raw_capture = PiRGBArray(camera, size=(cam_width, cam_height))

    # You can reuse the raw_capture to produce multiple arrays by emptying it with truncate(0) between captures
    raw_capture.truncate(0)
    try:
        # Create TCP socket
        conn = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

        # Try to connect to server
        conn.connect((IP, PORT))

    except Exception as ex:
        print("Socket Error>> ", ex)
        return None
    
    # Obtain a continuous frame and convert RGB to BGR because Python image format is BGR.
    for raw_frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):    
        # Convert raw frame data to array data
        frame = raw_frame.array
        try:
            # Send frame to server
            send_frame(conn, frame)

            # Receive message from server for their sync
            msg = conn.recv(10)
            
            # Verify that the server received well
            if str(msg, "utf-8") != "OK":
                break

        except IOError:
            break

        # Empty the array as above
        raw_capture.truncate(0)
        
    # Release connection & camera    
    conn.close()
    camera.close()
    
if __name__ == "__main__":
    init()
    run_cctv()
