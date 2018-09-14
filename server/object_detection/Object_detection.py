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

'''
type: function
name: init
description: initialize required constants variables
'''
def init():
    global addr, img_file_path, frame_queue, queue_size, android_connection
    print("init")

    ip = sock.gethostname()
    port = 9999
    addr = (ip, port)

    root_folder = os.path.dirname(os.path.abspath(__file__)) # Get root directory path
    img_file_path = os.path.join(root_folder, 'test.jpg')

    frame_queue = queue.Queue()
    queue_size = 30

    android_connection = False

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

def convert_to_base64(image):
    img_str = cv2.imencode('.png', image)[1].tostring()
    b64 = base64.b64encode(img_str)
    return b64.decode('utf-8')

def run_detector():
    global frame_queue, queue_size, android_connection, conn_android

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

    while True:
        # If frame queue is empty, then go to the next loop
        if frame_queue.empty() == True:
            continue
        #image = cv2.imread(PATH_TO_IMAGE)
        image = frame_queue.get()
        image_expanded = np.expand_dims(image, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})

        # Draw the results of the detection (aka 'visulaize the results')

        vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.80)

        # All the results have been drawn on image. Now display the image.
        #cv2.imshow('Object detector', image)

        # Press any key to close the image
        #if cv2.waitKey(1) == ord('q'):
        #    break

        if android_connection:
            width, height = image.shape[:2]
            #frame = cv2.resize(image, (int(height/4), int(width/4)))

            # HD Mode
            frame = cv2.resize(image, (774, 681))

            encoded = convert_to_base64(frame)
            outjson = {}
            outjson['img'] = encoded
            outjson['state'] = "Normal"
            json_data = json.dumps(outjson)
            write_utf8(str(json_data), conn_android)
            android_connection = False

    # Clean up
    #cv2.destroyAllWindows()

'''
type: function
name: get_cctv_frames
description: Get cctv frames from raspberry pi 
'''
def get_cctv_frames():
    global addr, frame_queue, queue_size
    print('Wating raspberry pi...')

    server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    print("Address: {0}".format(addr))
    server.bind(addr)
    
    print('listen')
    server.listen(1) # listen and wait for one client

    conn, addr = server.accept() # accept
    print("Client connected: {0}".format(addr))
 
    while True:
        data_len = recvall(conn, 16, dtype="string")
        print(data_len)
        img_bytes = recvall(conn, int(data_len), dtype="bytes")
        #data = np.fromstring(stringData, dtype='uint8')
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), 1)

        if frame_queue.qsize() < queue_size:
            frame_queue.put(img)
        else:
            frame_queue.get()
            frame_queue.put(img)

    server.close()
    cv2.destroyAllWindows()

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
            #print(buff)
            if buff == "Conn":
                android_connection = True
                #print("Android Connected")

            elif buff == "Exit":
                android_connection = False
                server.close()
                #print("Android Exited")
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