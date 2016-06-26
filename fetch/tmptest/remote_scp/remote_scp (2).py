#-*- coding:UTF-8 -*-
import paramiko
import os,datetime
import logging,time
from logging.handlers import TimedRotatingFileHandler
logdir=os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(logdir):
    os.makedirs(logdir)
logpath=os.path.join(logdir,'remote_scp.log')    

def init_log(): 
    '''功能描述：初始化日志参数'''
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d][%(levelname)s]:%(message)s")
    fileHandle = logging.handlers.RotatingFileHandler(logpath, maxBytes=(10*(1<<20)), backupCount=5)
    fileHandle.setFormatter(formatter)
    logger.addHandler(fileHandle)
    logger.addHandler(console)
init_log()


def remote_scp(host_ip,username,password,remote_dir,local_dir):
    while True:
        try:
            t = paramiko.Transport((host_ip,22))    
            t.connect(username=username, password=password)  
            sftp = paramiko.SFTPClient.from_transport(t) 
            rm_path_one=remote_dir
            rm_list_one=sftp.listdir(rm_path_one)
            count =0
            logging.info('begin to walk path %s' % rm_path_one)
            for item in rm_list_one:                
                rm_path_two=rm_path_one+r'/'+item
                rm_list_two=sftp.listdir(rm_path_two)
                logging.info('begin to walk path %s' % rm_path_two)
                for sub in rm_list_two:                
                    rm_path_three=rm_path_two+r'/'+sub
                    rm_list_three=sftp.listdir(rm_path_three)
                    logging.info('begin to walk path %s' % rm_path_three)
                    for m in rm_list_three:
                        try:                        
                            tmp_fpath=rm_path_three+r'/'+m
                            src=tmp_fpath
                            dst=os.path.join(local_dir,item,sub,m)
                            try:
                                if not os.path.exists(os.path.split(dst)[0]):
                                    os.makedirs(os.path.split(dst)[0])
                            except Exception,e:
                                logging.debug('create dir error %s'% str(e))
                            if os.path.exists(dst):
                                logging.info('file already exist ,%s' % dst)
                                
                            else:
                                sftp.get(src,dst)
                                count += 1
                                logging.info('success get file %s from remote and save at %s' % (src,dst)) 
                            try:
                                tag= False
                                while not tag:
                                    if os.path.getsize(dst) >1024:                                        
                                        tag = True
                                        sftp.remove(src)
                                        logging.info('remove file success %s '% src)
                                        break
                                    else:
                                        sftp.get(src,dst)
                            except Exception,e:
                                logging.debug('remove file %s error %s'% (src,str(e)))
                            logging.info('the success num is %d' % count)
                        except Exception,e:
                            logging.debug('get single file error %s' % str(e))
                    try:
                        sftp.rmdir(rm_path_three)
                        logging.info('success rm dir %s' % rm_path_three)
                    except Exception,e:
                        logging.debug('rm dir %s error %s' %(rm_path_three,str(e)))
                try:
                    sftp.rmdir(rm_path_two)
                    logging.info('success rm dir %s' % rm_path_two)
                except Exception,e:
                    logging.debug('rm dir %s error %s' %(rm_path_two,str(e)))
            #try:
                #sftp.rmdir(rm_path_one)
                #logging.info('success rm dir %s' % rm_path_one)
            #except Exception,e:
                #logging.debug('rm dir %s error %s' %(rm_path_one,str(e)))
            t.close()
            return True
        except Exception,e:
            logging.info('error msg is %s' % str(e))
            return False
        time.sleep(60)
if __name__ == '__main__':
    '''参数依次为：IP，用户名，密码，远程目录，本地保存目录；注意该处的函数仅仅处理三层目录结构，例如cjol/800/010/800010123.html'''
    remote_scp('123.58.128.216','user_00','Hick0000','/data/fetch/db/cjol',r'G:\datadb\cjol')