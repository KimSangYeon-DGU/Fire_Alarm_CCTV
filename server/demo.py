'''
this is a demo server app
'''
import os, cv2
import socket as sock
from PIL import Image
import numpy as np
import struct

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
    global addr, img_file_path
    print("init")

    ip = sock.gethostname()
    port = 9999
    addr = (ip, port)

    root_folder = os.path.dirname(os.path.abspath(__file__)) # Get root directory path
    img_file_path = os.path.join(root_folder, 'test.jpg')

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
name: connect_rberry
description: connect server with raspberry pi
'''
def connect_rberry():
    global addr
    print('Wating raspberry pi...')

    server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    print("Address: {0}".format(addr))
    server.bind(addr)
    
    print('listen')
    server.listen(1) # listen and wait for one client

    conn, addr = server.accept() # accept
    print("Client connected: {0}".format(addr))
    rv = 0
    while True:
        data_len = recvall(conn, 16, dtype="string")
        print(data_len)
        stringData = recvall(conn, int(data_len), dtype="bytes")
        data = np.fromstring(stringData, dtype='uint8')
        img = cv2.imdecode(np.frombuffer(data, np.uint8), 1)

        if img is not None:
            height, width = img.shape[:2]
            if height > 0 and width > 0:
                cv2.imshow("preview", img)

        if cv2.waitKey(1) == 27:
                    break
    server.close()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    init()
    #run()
    connect_rberry()
