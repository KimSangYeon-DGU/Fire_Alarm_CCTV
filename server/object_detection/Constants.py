import socket as sock
import os

IP = sock.gethostname()
CCTV_PORT = 9000
ANDR_PORT = 8000

CUR_DIR = os.getcwd()
REC_DIR = os.path.join(CUR_DIR, "record")

DB_ADDR = "DB Address"
PUSH_ADDR = "PUSH Address"
REG_ID = "Registration ID"
NOTIF_COUNT = 15
QUEUE_SIZE = 30