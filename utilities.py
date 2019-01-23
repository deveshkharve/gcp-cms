# logger to log information
# logs data with the timestamp and levels
import logging
import os
import datetime
import config as CONFIG
import re
import time
from logging.handlers import TimedRotatingFileHandler

LOG_FILE_DIRECTORY = CONFIG.LOG_FILE_DIRECTORY
if not os.path.exists(LOG_FILE_DIRECTORY):
    os.makedirs(LOG_FILE_DIRECTORY)

currDate = datetime.datetime.today().strftime('%Y-%m-%d')
LOG_FILENAME = CONFIG.LOG_FILEPATH + currDate + ".log"
LOG_FILENAME = os.path.join(LOG_FILE_DIRECTORY, LOG_FILENAME)
FORMAT = '%(asctime)s %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s'
# logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format=FORMAT)

logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler(LOG_FILENAME, when="midnight", interval=1, backupCount=5)
formatter = logging.Formatter(FORMAT)
fh = logging.FileHandler(LOG_FILENAME)
fh.setFormatter(formatter)
logger.addHandler(handler)




############################################################################################
## utilities function
############################################################################################

def isFloat(n):
    n = str(n)  # optional; make sure you have string
    return bool(re.match(r'^-?\d+(\.\d+)?$', n))  # bool is not strictly necessary

def xstr(s):
    if s is None:
        return ''
    return str(s)

def getDateFromLong(longDateTime):
    timeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(longDateTime)))
    return timeStr
