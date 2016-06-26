#-*- coding:utf-8 -*-

import logging,os
from logging.handlers import TimedRotatingFileHandler
from common import log_dir
#logdir=os.path.dirname(os.path.abspath(__file__))
logdir=log_dir
if not os.path.exists(logdir):
    os.makedirs(logdir)
logpath=os.path.join(logdir,'fetch_new2.log')

def init_log():  
    '''功能描述：初始化日志参数'''
    logger = logging.getLogger()
    console = logging.StreamHandler()
    # 命令行只输出 WARNING 以及以上级别
    console.setLevel(logging.WARNING)
    # 程序记录 DEBUG 以及以上级别的
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d][%(levelname)s]:%(message)s")
    #fileHandle = logging.handlers.RotatingFileHandler(logpath, maxBytes=(10*(1<<20)), backupCount=5)
    # fileHandle = logging.handlers.RotatingFileHandler(logpath, maxBytes=(1<<30), backupCount=5)
    fileHandle = logging.handlers.WatchedFileHandler(logpath)
    # 日志轮转有问题，不是每个进程都写在fetch.log 中，暂时不用日志轮转方式
    # fileHandle = logging.handlers.RotatingFileHandler(logpath)
    fileHandle.setFormatter(formatter)
    logger.addHandler(fileHandle)
    logger.addHandler(console)
init_log()
