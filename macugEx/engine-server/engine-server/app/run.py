# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_os()
monkey.patch_socket()
monkey.patch_thread(Event=True)
monkey.patch_time()
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from functools import wraps
from logging.handlers import RotatingFileHandler
from ssl import SSLError, SSLEOFError
from gevent import socket
import os
import sys
import logging

try:
    import ujson as json
except ImportError:
    import json

app = Flask('app')

sys.path.append('..')
import conf
from api.errno import E_server
from api import apiv1
from api import apiv2
from service_api.service import app as serv_app


def debuging(func, fail):
    @wraps(func)
    def debug_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            request_form = request.json if request.mimetype == 'application/json' else request.form if \
                request.form else json.loads(request.data) if request.data else {}
            logger.error('debug request: %s' % request_form, exc_info=True)
            return fail(E_server)

    return debug_wrapper


API_PREFIX = 'api_'


def add_view_func(module, pattern):
    for funcname in dir(module):
        if funcname.startswith(API_PREFIX):
            endpoint = funcname.split(API_PREFIX, 1)[1]
            raw_view_func = getattr(module, funcname)
            view_func = debuging(raw_view_func, module.failed) if conf.app['debug'] else raw_view_func
            app.add_url_rule(pattern % endpoint, endpoint, view_func, methods=['POST'])


add_view_func(apiv1, '/v1/%s')
add_view_func(apiv2, '/v2/%s')

app.register_blueprint(serv_app, url_prefix='/v1')

app.secret_key = os.urandom(24)
app.config['DEBUG'] = conf.app['debug']
app.config['SESSION_COOKIE_NAME'] = 'secret'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = conf.app['debug']
app.config['PROPAGATE_EXCEPTIONS'] = True

logger = logging.getLogger('app')
logfile = os.path.abspath(os.path.join(os.path.dirname(conf.__file__), conf.app['logfile']))
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=10)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s'))
File_logging.setLevel(conf.app['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(conf.app['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (SSLEOFError, SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if conf.app['debug']:
    printlog = logging.StreamHandler()
    printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
    printlog.setLevel(conf.app['loglevel'])
    logger.addHandler(printlog)

if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    server = WSGIServer(('', conf.app['port']), app, log=None, backlog=1024)
    server.serve_forever()
