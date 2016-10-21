# -*- coding: utf-8 -*-
from broker import Broker
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from gevent import get_hub

sys.path.append('..')

import conf

server_host = conf.agent['host']
request_port = conf.agent['request_port']
respound_port = conf.agent['respond_port']
channel_port = conf.agent['port']

if server_host != '127.0.0.1':
    server_host = '0.0.0.0'

logger = logging.getLogger('broker')
logfile = os.path.abspath(os.path.join(os.path.dirname(conf.__file__), conf.agent['logfile']))
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(conf.agent['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(conf.agent['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if not issubclass(exc_type, (KeyboardInterrupt, SystemExit, SystemError)):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if __name__ == "__main__":
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    broker = Broker(server_host, request_port, respound_port, channel_port, log=logger)
    print('Serving Start on %s port %s ...' % (server_host, channel_port))
    broker.run()
