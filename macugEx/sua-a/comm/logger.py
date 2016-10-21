# -*- coding: utf-8 -*-
# run.py 后台进程日志
import socket
import ssl
import sys
import gevent
import logging
from logging.handlers import RotatingFileHandler


def setup_daemon_logging(logging_name, logging_file, debug=False):
    logging_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger(logging_name)
    File_logging = RotatingFileHandler(logging_file, maxBytes=10 * 1024 * 1024, backupCount=10)
    File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s'))
    File_logging.setLevel(logging_level)
    logger.addHandler(File_logging)
    logger.setLevel(logging_level)

    if debug:
        printlog = logging.StreamHandler()
        printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
        printlog.setLevel(logging_level)
        logger.addHandler(printlog)

    def sys_exc_hook(exc_type, exc_value, exc_tb):
        if exc_type not in (KeyboardInterrupt,):
            logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))

    def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
        if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
            logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = sys_exc_hook
    gevent.get_hub().print_exception = gevent_exc_hook

    return logger
