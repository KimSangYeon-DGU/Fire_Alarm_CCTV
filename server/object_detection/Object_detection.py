################################Fire Detection Server ################################
#
# Author: Alex Kim
# Date: 9/28/18
# Description: 
# This is the Fire detection server using tensorflow object detection API.

# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import socket as sock
import threading
import queue
import json
import base64
import struct
import datetime
from firebase import firebase
from pyfcm import FCMNotification
import Constants

'''
Type: function
Name: init
Description: Initialize necessary variables and constants before running cctv.
'''
def init():
    global img_file_path, frame_queue, android_connected, HD, display_width, display_height, REC, fourcc, NOTIF, SAVE, IM_SHOW, fire_dir, fbase, cur_notif_time
    print("init")

    # Get root directory path
    root_folder = os.path.dirname(os.path.abspath(__file__))

    # Get test image file path
    img_file_path = os.path.join(root_folder, 'test.jpg')

    # Get fire directory path
    fire_dir = os.path.join(Constants.CUR_DIR, "fire")

    # Generate frame queue
    frame_queue = queue.Queue()

    # Set android connection flag that checks if android is connected to False.
    android_connected = False

    # Set HD mode flag to off
    HD = "off"

    # Initialize android camera width and height to None
    display_width = None
    display_height = None

    # Set record mode flag to False
    REC = False

    # Set push notification mode flag to False
    NOTIF = False

    # Set fire image save mode flag to False
    SAVE = False

    # Set image show mode flag that shows image to user using opencv window to False, if you can run this program in Non-GUI env., it should be False.
    IM_SHOW = False

    # Initialize fourcc to XVID for recording frame into .avi video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    # Generate Firebase object
    fbase = firebase.FirebaseApplication(Constants.DB_ADDR, None)

    # Set current notification time [date, minutes]
    cur_notif_time = ["", 0]

'''
Type: function
Name: write_utf8
Description: 
It is a function that is made separately to write messages to Android.
Encoding the message with uf-8 and transmitting the length and data in turn.
'''
def write_utf8(msg, socket):
    # Encode string to utf-8 to match both side's format
    encoded = msg.encode(encoding='utf-8')

    # Pack string of encoded message length to byte array
    socket.sendall(struct.pack('>i', len(encoded)))

    # Send encoded message to Android
    socket.sendall(encoded)
    
'''
Type: function
Name: read_utf8
Description: 
It is a function that is made separately to read messages from Android.
First, read the length of the message. Then, unpack the bytes.
After then, Read the message as long as it is, and return message in utf-8 string format
'''
def read_utf8(sock):
    # Read message bytes length
    len_bytes = recvall(sock, 4)

    # Unpack the bytes
    length = struct.unpack('>i', len_bytes)[0]

    # Read the message as long as it is. 
    encoded = recvall(sock, length)

    # Return message in utf-8 string format
    return str(encoded, encoding='utf-8')

'''
Type: function
Name: recvall
Description: 
It is a function that is made separately to read messages from Android.
Read the message repeatedly as long as it is.
Maximum buffer size is 4096, and it is known as the safest size without loss.
'''
def recvall(sock, size):
    # Set aside message chunks buffer
    received_chunks = []

    # Set buffer size to 4096
    buf_size = 4096

    # Set size of remaining to read to size param.
    remaining = size

    # Repeat until having finished reading the message.
    while remaining > 0:

        # Receive message from server by the remaining length
        received = sock.recv(min(remaining, buf_size))

        # If no message is received, raise an error.
        if not received:
            raise Exception('unexcepted EOF')

        # Append received message to chunk list
        received_chunks.append(received)

        # Subtract by the length of the received message.
        remaining -= len(received)

    # Return full message in the byte format
    return b''.join(received_chunks)

'''
Type: function
Name: recv_from_cctv
Description: 
It is a function that is made separately to read messages from CCTV.
It can read messages in a byte or string foramt
The buffer is sized by count.
'''
def recv_from_cctv(sock, count, dtype):
    # If data type to receive bytes, buf starts b''
    if dtype == "bytes":
        buf = b''
    # If data type to receive string, buf starts ''
    else:
        buf = ''

    # Read all message repeatdly by count
    while count:
        # Receive message
        newbuf = sock.recv(count)

        # If received message is null, return none
        if not newbuf: return None

        # If data tyde is string, decode the string into utf-8
        if dtype == "string":
            newbuf = newbuf.decode("utf-8")

        # Append chunk to full buffer
        buf += newbuf

        # Subtract length of message from count that represents total length to receive
        count -= len(newbuf)

    # Return full buffer
    return buf

'''
Type: function
Name: convert_to_base64
Description: 
The base64 library was used to encode image without using OpenCV in Android.
'''
def convert_to_base64(image):
    # Encode image with opencv and convert numpy array to bytes string
    img_str = cv2.imencode('.png', image)[1].tostring()

    # Encode bytes string using base64 library and it is decoded in android later.
    b64 = base64.b64encode(img_str)

    # Return utf-8 decoded image bytes string to convert string.
    return b64.decode('utf-8')

'''
Type: function
Name: set_video_writer
Description: 
This function is to initialize video writer when the day changes
'''
def set_video_writer(video_name, fourcc, FPS, width, height):
    return cv2.VideoWriter(video_name, fourcc, FPS, (width, height))

'''
Type: function
Name: send_push_notif
Description: 
This function is to send push notification to Android
'''
def send_push_notif(title, body):
    # Generate push service object
    push_service = FCMNotification(api_key=Constants.PUSH_ADDR)

    # Send push notif. to android and the notify_single_device returns result.
    ret = push_service.notify_single_device(registration_id=Constants.REG_ID, message_title=title, message_body=body)

    print(ret)

'''
Type: function
Name: save_fire_image
Description: 
This function is to save fire image.
'''
def save_fire_image(image, image_name, cam, ext):
    global fire_dir

    # Get image directory path by camera id
    cam_dir = os.path.join(fire_dir, cam)

    # Get image path to save
    img_path = os.path.join(cam_dir, image_name+"."+ext)

    # Save fire image
    cv2.imwrite(img_path, image)

'''
Type: function
Name: send_fire_image
Description: 
This function is to send archived fire image to Android.
'''
def send_fire_image(cam, date):
    global display_width, display_height, fire_dir

    # Get image directory path by camera id
    cam_dir = os.path.join(fire_dir, cam)

    # Read image in camera directory path
    frame = cv2.imread(os.path.join(cam_dir, date+".png"))

    json_data = convert_img_to_json(frame, "Fire")

    # Send json data to the android client
    write_utf8(str(json_data), conn_android)

'''
Type: function
Name: update_log_db
Description: 
This function is to update log database in firebase.
'''
def update_log_db(image_name, cam):
    global fbase
    
    # Set target database path
    target_path = "/users/user1/"+cam+"/"

    # Get log data to update
    result = fbase.get(target_path + "log", None)

    # Append new data to result["date"]
    result["date"].append(image_name)

    # Add 1 to total number of logs
    result["num_of_logs"] = 1 + int(result["num_of_logs"])

    # Update database
    result = fbase.put(target_path, "log", result)

'''
Type: function
Name: send_data_from_firebase
Description: 
This function is to send data get from firebase to android
'''
def send_data_from_firebase(cam, title):
    global conn_android, fbase

    # Set user name to "user1", it should be able to changed dynamically later if the multiple user functionality is added.
    user_name = "user1"

    # Get data from firebase
    outjson = fbase.get("/users/"+user_name+"/"+str(cam)+"/"+str(title), None)

    # Print json data
    print(outjson)

    # Send json to android client
    write_utf8(str(outjson), conn_android)

'''
Type: function
Name: convert_img_to_json
Description: 
This function is to convert image into json data for sending to Android.
'''
def convert_img_to_json(image, state):
    global HD, display_width, display_height 

    # Create empty json
    outjson = {}

    # Resize image according to state and HD mode
    if state == "Normal":
        if HD == "on": 
            rsz_image = cv2.resize(image, (int(display_height/2), int(display_width/2)))
        else:
            rsz_image = cv2.resize(image, (int(display_height/6), int(display_width/6)))
    elif state == "Fire":
        # Resize for smooth communication
        rsz_image = cv2.resize(image, (int(display_width/4), int(display_height/4)))

    # Encode image to string
    encoded = convert_to_base64(rsz_image)

    # Assign encoded image according to state.
    if state == "Normal":
        outjson['img'] = encoded
    elif state == "Fire":
        outjson['encoded'] = encoded

    # Assign state to "state" key
    outjson['state'] = state

    # Dump json data 
    json_data = json.dumps(outjson)

    return json_data

'''
Type: function
Name: check_notif_possible
Description: 
This function is to check whether to send push notification to Android using time difference
'''
def check_notif_possible():
    global cur_notif_time

    # Get current time in a string format
    splt_time = str(datetime.datetime.now()).split(" ")

    # Split date
    date = splt_time[0]

    # Split hour, minute respectively
    hour = splt_time[1][0:2]
    minute = splt_time[1][3:5]

    # Convert to minutes.
    new_time = int(hour) * 60 + int(minute)

    # Return True if different date is or date is the same but minute differences are more than 10 minutes
    if cur_notif_time[0] != date:
        # Save new date
        cur_notif_time[0] = date
        return True
    else:
       if Constants.NOTIF_MINIUTE <= (new_time - cur_notif_time[1]):
           # Save new minutes
           cur_notif_time[1] = new_time
           return True
    return False

'''
Type: function
Name: run_detector
Description: 
This function is to detect fire and process requests from cctv or android.
It also sends push notification to Android client.
'''
def run_detector():
    global frame_queue, NOTIF, SAVE, IM_SHOW
    # This is needed since the notebook is stored in the object_detection folder.
    sys.path.append("..")

    # Import utilites
    from utils import label_map_util
    from utils import visualization_utils as vis_util

    # Name of the directory containing the object detection module we're using
    MODEL_NAME = 'inference_graph'
    IMAGE_NAME = 'test.jpg'

    # Grab path to current working directory
    CWD_PATH = os.getcwd()

    # Path to frozen detection graph .pb file, which contains the model that is used
    # for object detection.
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,'training','label_map.pbtxt')

    # Path to image
    PATH_TO_IMAGE = os.path.join(CWD_PATH,IMAGE_NAME)

    # Number of classes the object detector can identify
    NUM_CLASSES = 1

    # Load the label map.
    # Label maps map indices to category names, so that when our convolution
    # network predicts `5`, we know that this corresponds to `king`.
    # Here we use internal utility functions, but anything that returns a
    # dictionary mapping integers to appropriate string labels would be fine
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    # Load the Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        sess = tf.Session(graph=detection_graph)

    # Define input and output tensors (i.e. data) for the object detection classifier

    # Input tensor is the image
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Output tensors are the detection boxes, scores, and classes
    # Each box represents a part of the image where a particular object was detected
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represents level of confidence for each of the objects.
    # The score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

    # Number of objects detected
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Load image using OpenCV and
    # expand image dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value

    # Set warning count to zero and it is made to determine whether to send push notif. or not 
    warn_count = 0

    # Set safe count to zero and it is made to determine whether to send push notif. or not 
    safe_count = 0
    while True:
        # If frame queue is empty, then go to the next loop
        if frame_queue.empty() == True:
            continue
        
        # Get frame from frame queue
        image = frame_queue.get()

        # Copy frame for other tasks.
        frame = image.copy()

        # Expand image for fire detection.
        image_expanded = np.expand_dims(image, axis=0)
        
        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        det_ret_list = vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.80)

        # Check whether to show the image. if you run this program in Non-GUI env., it should be False.
        if IM_SHOW:
            cv2.imshow('Object detector', image)
            if cv2.waitKey(1) == ord('q'):
                break

        # if the length of det_ret_list is not zero, object(s) is detected.
        if len(det_ret_list):

            # Search fire among detected objects.
            for det_ret in det_ret_list:
                cats_list = det_ret["cats"]
                
                for cats_str in cats_list: 
                    splt_cat = cats_str.split(":")

                    # If name of category is fire, the check vars like warn_count, safe_count set specific value for push notification
                    if splt_cat[0] == "fire":
                        warn_count+=1
                        safe_count = 0
                        print(cats_str)
                    else:
                        safe_count += 1
        # If warn count is bigger than NOTIF COUNT, send push notification to Android.
        if Constants.NOTIF_COUNT <= warn_count:
            warn_count = 0
            # Check if the notification is possible.
            if check_notif_possible():
                # Call function using thread.
                # first args is title and another is content. 
                notif_thread = threading.Thread(target=send_push_notif, args=("A fire has been detected", "Please check your CCTV App", ))
                notif_thread.start()
                notif_thread.join()

            # Check if the save is possible
            if SAVE:
                # Save fire image using datetime
                splt_time = str(datetime.datetime.now()).split(" ")
                image_name = "{0}_{1}_{2}_{3}".format(splt_time[0], splt_time[1][0:2], splt_time[1][3:5], splt_time[1][6:8])
                update_log_db(image_name, "CAM01")
                save_fire_image(image, image_name, "CAM01", "png")

        # If safe count is bigger than NOTIF COUNT, the warn count is set to zero.
        if Constants.NOTIF_COUNT <= safe_count:
            warn_count = 0

    # Close the window to show image.
    if IM_SHOW:
        cv2.destroyAllWindows()

'''
type: function
name: wait_cctv
description: 
This function is to get frames from CCTV.
And record frames in a avi video format.
'''
def wait_cctv():
    global frame_queue, REC, fourcc

    # Set to pre_date to "" and it represents video name.
    pre_date = ""
    while True:
        print('Wating cctv...')    

        # Generate socket to communicate cctv socket
        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

        # Bind socket
        print("Address: {0}: {1}".format(Constants.IP, Constants.CCTV_PORT))
        server.bind((Constants.IP, Constants.CCTV_PORT))
        
        # Listen socket
        print('listen')
        server.listen(1) # listen and wait for one client

        # Accept CCTV socket
        conn, addr = server.accept() # accept
        print("cctv connected: {0}".format(addr))
        
        while True:
            # Get length of message first, and then message
            # If error occurs, then socket is closed.
            try:
                data_len = recv_from_cctv(conn, 16, dtype="string")
                #print(data_len)
                img_bytes = recv_from_cctv(conn, int(data_len), dtype="bytes")
                
            except ConnectionResetError:
                print("The cctv was forcefully disconnected.")
                server.close()
                break
            except Exception:
                print("The cctv was forcefully disconnected.")
                server.close()
                break

            # Decode bytes image to numpy image
            frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), 1)
            
            # Record frames.
            if REC:
                # Record videos by date and remove the oldest files if there are more than 60 recorded files.
                fr_height, fr_width = frame.shape[:2]
                cur_date = datetime.datetime.date(datetime.datetime.now())
                if pre_date != cur_date:
                    file_names = os.listdir(Constants.REC_DIR)
                    file_names.sort()
                    num_of_files = len(file_names)
                    if num_of_files > Constants.REC_FILE_NUM:
                        os.remove(os.path.join(Constants.REC_DIR, file_names[0]))
                    video = set_video_writer(os.path.join(Constants.REC_DIR, str(cur_date)+".avi"), fourcc, 20, width=fr_width, height=fr_height)
                pre_date = cur_date
                video.write(frame)

            # Insert frame into frame queue to detect fire at run_detector()
            # If size of frame_queue is bigger than specified QUEUE_SIZE, the first frame is extracted.
            if frame_queue.qsize() < Constants.QUEUE_SIZE:
                frame_queue.put(frame)
            else:
                frame_queue.get()
                frame_queue.put(frame)

    # Video close.
    if REC:
        video.release()   

'''
type: function
name: wait_android
description: 
This function is to communicate with android client.
Send frame, log, and info data to android. 
'''
def wait_android():
    global img_file_path, android_connected, conn_android, HD, display_width, display_height, frame_queue
    
    while True:
        print("Wating android...")

        # Generate socket to communicate android socket.
        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM) 

        # Bind socket.
        server.bind((Constants.IP, Constants.ANDR_PORT)) 

        # Listen socket.
        print('listen to android connection')
        server.listen(1) # listen and wait for one client

        # Accept socket.
        conn_android, _ = server.accept()

        while True:
            # Read message from android.
            # If error occurs, the socket is closed.
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

            # Convert msg to the json format.
            msg = json.loads(msg)

            # Get status in json data
            status = msg["status"]

            # Process according to status
            # conn: Send frame to android
            # exit: Close the socket.
            # info: Send info data get from firebase to android.
            # log: Send log data get from firebase to android.
            # fire: Send fire image to android.
            if status == "conn":
                android_connected = True
                HD = msg["hd"]
                display_width = msg["width"]
                display_height = msg["height"]       
                if frame_queue.qsize():
                    frame = frame_queue.get()
                else:
                    break

                json_data = convert_img_to_json(frame, "Normal")
               
                write_utf8(str(json_data), conn_android)
                
            elif status == "exit":
                android_connected = False
                server.close()
                break

            elif status == "info":
                send_data_from_firebase(msg["camera"], status)
                break

            elif status == "log":
                send_data_from_firebase(msg["camera"], status)
                break

            elif status == "fire":
                display_width = msg["width"]
                display_height = msg["height"]
                send_fire_image(msg["camera"], msg["date"])
                break
    
if __name__ == "__main__":
    init()
    t1 = threading.Thread(target=wait_cctv)
    t2 = threading.Thread(target=wait_android)
    t1.start()
    t2.start()
    run_detector()
    t1.join()
    t2.join()