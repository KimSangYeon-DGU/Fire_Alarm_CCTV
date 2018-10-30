import socket as sock
import os

IP = sock.gethostname()
CCTV_PORT = 9000
ANDR_PORT = 8000

CUR_DIR = os.getcwd()
REC_DIR = os.path.join(CUR_DIR, "record")

DB_ADDR = "Database server address"
PUSH_ADDR = "Push notification server address"
REG_ID = "Registration ID"
NOTIF_COUNT = 4
QUEUE_SIZE = 30
REC_FILE_NUM = 60

NOTIF_MINIUTE = 10