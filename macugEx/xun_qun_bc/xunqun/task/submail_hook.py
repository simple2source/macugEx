# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_all(Event=True, dns=False)
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from hashlib import md5
from logging.handlers import RotatingFileHandler
import logging
import sys
import ssl
import socket

sys.path.append('..')
from core.db import db
import setting

app = Flask(__name__)

key = '0189178cd266829ec086e034e64b95f7'


@app.route('/submail_hook', methods=['POST'])
def send_mail():
    params = request.form.copy()
    if md5(params['token'] + key).hexdigest() == params['signature']:
        del params['token']
        del params['signature']
        params['timestamp'] = float(params['timestamp'])
        db.submail.insert_one(params)
    return 'success'


logger = logging.getLogger('task')
logfile = setting.app['logfile']
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=10)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s'))
File_logging.setLevel(setting.app['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(setting.app['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    server = WSGIServer(('', 8081), app, log=None, backlog=1024)
    server.serve_forever()
