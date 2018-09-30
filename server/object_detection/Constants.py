import socket as sock
import os

IP = sock.gethostname()
CCTV_PORT = 9000
ANDR_PORT = 8000

CUR_DIR = os.getcwd()
REC_DIR = os.path.join(CUR_DIR, "record")

DB_ADDR = "https://database-9579c.firebaseio.com/"
PUSH_ADDR = "AAAALAmx7fk:APA91bF5nUol6YBNmKvudG4YTC_AgOcZ0fxaoeJDWsVdDWXRd2JqDUR_9My3KzE_xqBKoWUHkKO4_f3j2hTFmvqj3glraPZHoR-3-6xMxzHaZt-bQL2KFE3_ds6ATAcBUggw18e7fbWM"
REG_ID = "cE-v-DzRduI:APA91bG3d7KM0BKJV4OwLPm2fJnRcsYHqPXefAoyPgQwbL-e0TEaZOgQImQw25vZONk9k4YPkZFeE4UnvJdPvfivzTFZP-ZJfikx6FKRffCGOySVFQx4SRccT0WaUANHDH8oQOjUr2b4"
NOTIF_COUNT = 4
QUEUE_SIZE = 30
REC_FILE_NUM = 60

NOTIF_MINIUTE = 10