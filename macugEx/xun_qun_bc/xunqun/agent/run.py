# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all(Event=True, dns=False)
from broker import Broker
import sys
import ssl
import socket
import logging
from logging.handlers import RotatingFileHandler
from gevent import get_hub

sys.path.append('..')

import setting

server_host = setting.broker['host']
request_port = setting.broker['request_port']
respound_port = setting.broker['respond_port']
channel_port = setting.broker['channel_port']

if server_host != '127.0.0.1':
    server_host = '0.0.0.0'

logger = logging.getLogger('broker')
logfile = setting.broker['logfile']
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(setting.broker['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(setting.broker['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if __name__ == "__main__":
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    broker = Broker(server_host, request_port, respound_port, channel_port, log=logger)
    broker.run()
