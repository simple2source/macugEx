# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_os()
monkey.patch_socket()
monkey.patch_thread(Event=True)
monkey.patch_time()
import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, redirect, request, session, render_template, abort
from flask_scrypt import generate_password_hash
from hashlib import md5
from ssl import SSLError, SSLEOFError
from gevent import socket
import urllib

sys.path.append('..')
import conf
from core.db import db
from core.buffer import ExpireBuffer
from admin import app as admin_app
from docs import app as docs_app

app = Flask('web', template_folder='templates')

app.register_blueprint(admin_app)
app.register_blueprint(docs_app)

login_cache = ExpireBuffer(expire=43200, check_cycle=43200)


def vertify_session_login():
    if 'login_key' not in session or session['login_key'] not in login_cache:
        return False
    else:
        return True


# 除了 login 外的权限验证
@app.before_request
def request_login():
    path_prefix = request.path.split('/', 2)[1]
    if path_prefix not in ('login', 'logout', 'static', 'favicon.ico'):
        if not vertify_session_login():
            return redirect('login?ref=' + request.path)
        permissions = session['permissions']
        request.permissions = permissions
        if path_prefix == 'docs':
            if 'document' not in permissions and 'admin' not in permissions:
                return abort(403)


salt = conf.admin['salt']


@app.route('/')
def index():
    return redirect('/admin')


# 验证 login 登陆
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_failed = 0
    ref = request.args.get('ref')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = db.admin.find_one({'_id': username, 'password': generate_password_hash(password, salt)},
                                     {'permissions': 1, 'nickname': 1})
            if user:
                login_key = os.urandom(12).encode('base64')
                login_cache.update(login_key)
                session['login_key'] = login_key
                session['username'] = username
                session['nickname'] = user.get('nickname')
                session['permissions'] = user['permissions']
                db.admin.update_one({'_id': username}, {'$set': {'lasttime': datetime.now()}})
                if request.args.get('ref'):
                    return redirect(request.args['ref'])
                return redirect('/')
        login_failed = 1
    return render_template('login.html', ref=ref, login_failed=login_failed)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return 'success'


app.secret_key = os.urandom(24)
app.config['DEBUG'] = conf.admin['debug']
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = conf.admin['debug']
app.config['PROPAGATE_EXCEPTIONS'] = True

logger = logging.getLogger('web')
logfile = os.path.abspath(os.path.join(os.path.dirname(conf.__file__), conf.admin['logfile']))
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=10)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s'))
File_logging.setLevel(conf.admin['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(conf.admin['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (SSLEOFError, SSLError, socket.error, KeyboardInterrupt, SystemExit, SystemError):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if conf.admin['debug']:
    printlog = logging.StreamHandler()
    printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
    printlog.setLevel(conf.admin['loglevel'])
    logger.addHandler(printlog)

if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    host = '0.0.0.0' if conf.admin['host'] != '127.0.0.1' else conf.admin['host']
    server = WSGIServer((host, conf.admin['port']), app, log=None, backlog=100000)
    print('Serving Start on %s port %s ...' % (host, conf.admin['port']))
    server.serve_forever()
