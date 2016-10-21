# -*- coding: utf-8 -*-
"""
腕表gps测试用功能
"""
from gevent import monkey, get_hub

monkey.patch_all(Event=True, dns=False)
from gevent.pywsgi import WSGIServer
import ssl
import socket
import gevent
import logging
from logging.handlers import RotatingFileHandler
import sys

sys.path.append('../..')
from loop import gps_strategy_loop
from web import app

# app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

logger = logging.getLogger('gps_strategy')

logfile = 'gps_strategy.log'
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(logging.INFO)
logger.addHandler(File_logging)
logger.setLevel(logging.INFO)


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    gevent.spawn(gps_strategy_loop)
    server = WSGIServer(('', 12345), app, log=None, backlog=1024)
    server.serve_forever()
