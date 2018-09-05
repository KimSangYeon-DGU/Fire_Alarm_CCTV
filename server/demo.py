'''
this is a demo server app
'''
import os
import socket as sock


'''
name: init
description: initialize required constants variables
'''
def init():
    global host, img_file_path
    print("init")

    addr = "your server ip"
    port = 9999
    host = (addr, port)

    root_folder = os.path.dirname(os.path.abspath(__file__)) # Get root directory path
    img_file_path = os.path.join(root_folder, 'test.jpg')

'''
name: run
description: run server app
'''
def run():
    global host, img_file_path
    print("run")

    server = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # initialize server socket
    server.bind(host) # socket bind

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

if __name__ == "__main__":
    init()
    run()