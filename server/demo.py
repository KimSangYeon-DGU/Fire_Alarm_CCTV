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

'''
type: function
name: run
description: run server app
'''
def run():
    global addr, img_file_path
    print("run")

    server = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # initialize server socket
    server.bind(addr) # socket bind

    print('listen')
    server.listen(1) # listen and wait for one client

    conn, addr = server.accept() # accept
    print("Client connected: {0}".format(addr))

    # Send test image
    with open(img_file_path, 'rb') as fp:
        data = fp.read()
        ret = conn.sendall(data)
        print(ret)
    
    server.close()

'''
type: function
name: wait_cctv
description: wait raspberry pi connection
'''
def wait_cctv():
    global addr, android_connection, conn_android
    print('Wating raspberry pi...')

    server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    print("Address: {0}".format(addr))
    server.bind(addr)
    
    print('listen to cctv connection')
    server.listen(1) # listen and wait for one client

    conn_cctv, addr = server.accept() # accept
    print("Client connected: {0}".format(addr))

    while True:
        data_len = recvall(conn_cctv, 16, dtype="string")
        #print(data_len)
        img_bytes = recvall(conn_cctv, int(data_len), dtype="bytes")
        #data = np.fromstring(str(img_bytes), dtype='uint8')
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), 1)

        if img is not None:
            height, width = img.shape[:2]
            if height > 0 and width > 0:
                cv2.imshow("preview", img)

        if cv2.waitKey(1) == 27:
                break
        
        #print(data_len.ljust(16).encode("utf-8"))
        #print(len(img_bytes))

        if android_connection:
            #conn_android.send("Hello".encode("utf-8"))
            #tmp_send = str(len(stringData)).ljust(16).encode("utf-8")
            #print(tmp_send)
            #p = struct.pack('!i', len(stringData))
            conn_android.send(data_len.ljust(16).encode("utf-8"))
            conn_android.send(img_bytes)
            #print(len(img_bytes))
        
            #conn_android.send(str(img).encode("utf-8"))    
            #conn_android.send(pickle.dumps(img))
            android_connection = False
            #conn_android.send(str("End"))


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
    wait_cctv()
    t.join()
    #run()
    #connect_android()
    
