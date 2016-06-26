#-*- conding:UTF-8 -*-
import os,logging,time
import paramiko
from logging.handlers import TimedRotatingFileHandler
def init_log():    
    logger = logging.getLogger()    
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d][%(levelname)s]:%(message)s")
    fileHandle = logging.handlers.RotatingFileHandler('monitor.log', maxBytes=(10*(1<<20)), backupCount=5)
    fileHandle.setFormatter(formatter)
    logger.addHandler(fileHandle) 
    logger.addHandler(console)
init_log()

def update_file(machine=[],src='',dst=''):
    try:
        client = paramiko.Transport((machine[0], 22))
        client.connect(username = machine[1], password = machine[2])
        sftp = paramiko.SFTPClient.from_transport(client)
        dst_dir=os.path.split(dst)[0]
        try:
            sftp.mkdir(dst_dir)
        except:
            pass
        sftp.put(src,dst)
        client.close()
        logging.info('success move file to %s' % machine[0])
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False

fpath ='/data/spider/cookie/cjol.txt'
org_time = os.path.getmtime(fpath)

while True:
    try:
        newtime=os.path.getmtime(fpath)
        if newtime>org_time:
            org_time=newtime
            logging.info('file modified')
            update_file(['115.231.92.102','user_00','User00sp'],fpath,'/data/fetch/cookie/cjol.txt')
            update_file(['115.231.92.103','user_00','User00sp'],fpath,'/data/fetch/cookie/cjol.txt')
            #os.system("/data/spider/restart.sh cjol")
        else:
            logging.info('file no update')
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
    time.sleep(30)
        
    
