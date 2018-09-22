######## Image Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 1/15/18
# Description: 
# This program uses a TensorFlow-trained classifier to perform object detection.
# It loads the classifier uses it to perform object detection on an image.
# It draws boxes and scores around the objects of interest in the image.

## Some of the code is copied from Google's example at
## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

## and some is copied from Dat Tran's example at
## https://github.com/datitran/object_detector_app/blob/master/object_detection_app.py

## but I changed it to make it more understandable to me.

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
type: function
name: init
description: initialize required constants variables
'''
def init():
    global img_file_path, frame_queue, android_connection, HD, display_width, display_height, REC, fourcc
    print("init")

    root_folder = os.path.dirname(os.path.abspath(__file__)) # Get root directory path
    img_file_path = os.path.join(root_folder, 'test.jpg')

    frame_queue = queue.Queue()

    android_connection = False

    HD = "off"
    display_width = None
    display_height = None
    REC = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')


def write_utf8(msg, socket):
    encoded = msg.encode(encoding='utf-8')
    socket.sendall(struct.pack('>i', len(encoded)))
    socket.sendall(encoded)

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
name: recvall
description: receive all packets by spliting total stream to 4096
the dtype modes are string and bytes, the bytes mode is to read image byte array
and the string mode is to read the length of total packets
'''
def recv_from_cctv(sock, count, dtype):

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


def convert_to_base64(image):
    img_str = cv2.imencode('.png', image)[1].tostring()
    b64 = base64.b64encode(img_str)
    return b64.decode('utf-8')

def set_video_writer(video_name, fourcc, FPS, width, height):
    global video

    video = cv2.VideoWriter(video_name, fourcc, FPS, (width, height))

def send_push_notif(title, body):
    push_service = FCMNotification(api_key=Constants.PUSH_ADDR)
    ret = push_service.notify_single_device(registration_id=Constants.REG_ID, message_title=title, message_body=body)
    print(ret)
    
def run_detector():
    global frame_queue, android_connection, conn_android, HD, display_width, display_height, video, REC, fourcc

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

    pre_date = ""
    warning_count = 0
    safe_count = 0
    while True:
        # If frame queue is empty, then go to the next loop
        if frame_queue.empty() == True:
            continue
        #image = cv2.imread(PATH_TO_IMAGE)
        image = frame_queue.get()
        frame = image.copy()
        image_expanded = np.expand_dims(image, axis=0)
        
        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        #print("boxes: " + str(boxes[0]))
        #print("classes: " + str(classes[0]))
        #print("num: "+str(num[0]))
        det_ret_list = vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.80)

        if 0 < len(det_ret_list):
            for det_ret in det_ret_list:
                cats_list = det_ret["cats"]
                for cats_str in cats_list: 
                    splt_cat = cats_str.split(":")
                    #print("category:{0}, prob:{1}".format(splt_cat[0], splt_cat[1]))
                    if splt_cat[0] == "fire":
                        warning_count+=1
                        safe_count = 0
                        print(warning_count)
                    else:
                        safe_count += 1
                
        if warning_count >= Constants.NOTIF_COUNT:
            notif_thread = threading.Thread(target=send_push_notif, args=("A fire has been detected", "Please check your CCTV App", ))
            notif_thread.start()
            notif_thread.join()
            warning_count = 0

            splt_time = str(datetime.datetime.now()).split(" ")
            
            image_name = "{0}_{1}_{2}_{3}".format(splt_time[0], splt_time[1][0:2], splt_time[1][3:5], splt_time[1][6:8])

            update_log_db(image_name, "CAM01")
            save_fire_image(image, image_name, "CAM01", "png")
    
        if safe_count >= Constants.NOTIF_COUNT:
            warning_count = 0

        if REC:
            cur_date = datetime.datetime.date(datetime.datetime.now())
            if pre_date != cur_date:
                file_names = os.listdir(Constants.REC_DIR)
                file_names.sort()
                num_of_files = len(file_names)
                if num_of_files > 3:
                    os.remove(os.path.join(Constants.REC_DIR, file_names[0]))
                set_video_writer(os.path.join(Constants.REC_DIR, str(cur_date)+".avi"), fourcc, 30, width=640, height=480)
            pre_date = cur_date
            video.write(frame)

        if android_connection:
            #frame = cv2.resize(image, (int(height/4), int(width/4)))

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

    video.release()

def save_fire_image(image, image_name, cam, ext):
    fire_dir = os.path.join(Constants.CUR_DIR, "fire")
    cam_dir = os.path.join(fire_dir, cam)
    img_path = os.path.join(cam_dir, image_name+"."+ext)
    cv2.imwrite(img_path, image)

def update_log_db(image_name, cam):
    fb = firebase.FirebaseApplication(Constants.DB_ADDR, None)
    result = fb.get("/users/user1/"+cam+"/log", None)

    result["date"].append(image_name)
    result["num_of_logs"] = 1 + int(result["num_of_logs"])
    result = fb.put("/users/user1/CAM01", "log", result)

def send_fire_image(cam, date):
    global display_width, display_height

    fire_dir = os.path.join(Constants.CUR_DIR, "fire")
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
    global conn_android

    print(cam)
    fb = firebase.FirebaseApplication(Constants.DB_ADDR, None)
    user_name = "user1"
    outjson = fb.get("/users/"+user_name+"/"+str(cam)+"/"+str(title), None)
    print(outjson)
    write_utf8(str(outjson), conn_android)

'''
type: function
name: get_cctv_frames
description: Get cctv frames from raspberry pi 
'''
def get_cctv_frames():
    global frame_queue

    while True:
        print('Wating cctv...')

        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        print("Address: {0}: {1}".format(Constants.IP, Constants.CCTV_PORT))
        server.bind((Constants.IP, Constants.CCTV_PORT))
        
        print('listen')
        server.listen(1) # listen and wait for one client

        conn, addr = server.accept() # accept
        print("cctv connected: {0}".format(addr))

        while True:
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

            ##data = np.fromstring(stringData, dtype='uint8')
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), 1)
            cv2.imshow('Object detector', img)
            if cv2.waitKey(1) == ord('q'):
                break

            if frame_queue.qsize() < Constants.QUEUE_SIZE:
                frame_queue.put(img)
            else:
                frame_queue.get()
                frame_queue.put(img)

        cv2.destroyAllWindows()

'''
type: function
name: wait_cctv
description: wait android connection
'''
def wait_android():
    global img_file_path, android_connection, conn_android, HD, display_width, display_height

    while True:
        print("Wating android...")

        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # initialize server socket
        server.bind((Constants.IP, Constants.ANDR_PORT)) # socket bind

        print('listen to android connection')
        server.listen(1) # listen and wait for one client

        conn_android, _ = server.accept() # accept

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
            #print(status)
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
    t1 = threading.Thread(target=get_cctv_frames)
    t2 = threading.Thread(target=wait_android)
    t1.start()
    t2.start()
    run_detector()
    t1.join()
    t2.join()