# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append('..')
from comm.db import db
from json import dumps
from comm.buffer import ExpireBuffer
from flask_scrypt import generate_password_hash
from flask import Flask, request, render_template, session, redirect, abort
from datetime import datetime


PROG_DIR = os.path.dirname(os.path.abspath(__file__))


try:
    import conf
except ImportError:
    import sys

    sys.path.append('..')
    try:
        import conf
    except ImportError:
        import shutil

        APP_DIR = os.path.join(PROG_DIR, '../')
        shutil.copyfile('%s/conf.sample' % APP_DIR, '%s/conf.py' % APP_DIR)
        import conf

from comm.logger import setup_daemon_logging

admin = Flask('admin')

login_cache = ExpireBuffer(expire=43200, check_cycle=43200)
salt = conf.admin['salt']
lasttime = ''


def verify_session_login():
    if 'login_key' not in session or session['login_key'] not in login_cache:
        return False
    else:
        return True


@admin.before_request
def request_login():
    path_prefix = request.path.split('/', 2)[1]
    if path_prefix not in ('login', 'logout', 'static', 'favicon.ico'):
        if not verify_session_login():
            return redirect('login')


@admin.route('/')
def index():
    menubar_list = [
        {
            '_id': 'base_info',
            'name': u'校友',
            'icon': 'fa-info-circle',
            'submenubar': {
                'users': {
                    'name': u'校友管理'
                }
            }
        },
        {
            '_id': 'base_company',
            'name': u'校企',
            'icon': 'fa-info-circle',
            'submenubar': {
                'company': {
                    'name': u'校企管理'
                }
            }
        },
        {
            '_id': 'base_alum',
            'name': u'校友会',
            'icon': 'fa-info-circle',
            'submenubar': {
                'association': {
                    'name': u'校友会管理'
                }
            }
        },
        {
            '_id': 'base_news',
            'name': u'校友资讯',
            'icon': 'fa-info-circle',
            'submenubar': {
                'news': {
                    'name': u'资讯信息管理'
                }
            }
        },
        {
            '_id': 'base_quote',
            'name': u'城哥语录',
            'icon': 'fa-info-circle',
            'submenubar': {
                'quote': {
                    'name': u'语录管理'
                }
            }
        },
        {
            '_id': 'base_donate',
            'name': u'校友捐赠',
            'icon': 'fa-info-circle',
            'submenubar': {
                'donate': {
                    'name': u'捐款管理'
                }
            }
        }
    ]
    return render_template('admin.html', menubar=menubar_list, server_uri=conf.app['base_url'])


@admin.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get('username')
    if request.method == 'GET':
        user = db.admin.find_one({'_id': username})
        global lasttime
        user['lasttime'] = lasttime
        if not user:
            session.clear()
            return abort(403)
        return dumps(user)
    else:
        for limit in ('lasttime', 'maketime', '_id'):
            if limit in request.params:
                return abort(403)
        result = db.admin.update_one({'_id': username}, {'$set': request.params})
        if result.modified_count == 1:
            return 'success'
        else:
            session.clear()
            return abort(403)


@admin.route('/create', methods=['POST'])
def admin_create():
    form_data = request.form.to_dict()
    username = form_data.get('username')
    password = form_data.get('password')
    exist = db.admin.find_one({'_id': username})
    if exist:
        return 'already exist'
    if username and password:
        try:
            maketime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = db.admin.insert({'_id': username, 'password': generate_password_hash(password, salt),
                                      'maketime': maketime})
            if result:
                return 'success', 200
        except Exception as e:
            return 'create error'
    return 'username or password empty'


@admin.route('/modify', methods=['POST'])
def modify():
    form_data = request.form.to_dict()
    username = form_data.get('_id')
    password = form_data.get('password')
    if username and password:
        db.admin.update_one({'_id': username}, {'$set': {'password': generate_password_hash(password, salt)}})
        return 'success'


@admin.route('/login', methods=['GET', 'POST'])
def login():
    login_failed = 0
    ref = request.args.get('ref')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = db.admin.find_one({'_id': username, 'password': generate_password_hash(password, salt)})
            if user:
                login_key = os.urandom(12).encode('base64')
                login_cache.update(login_key)
                session['login_key'] = login_key
                session['username'] = username
                global lasttime
                lasttime = user.get('lasttime')
                login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db.admin.update_one({'_id': username}, {'$set': {'lasttime': login_time}})
                if request.args.get('ref'):
                    return redirect(request.args['ref'])
                return redirect('/')
        login_failed = 1
    return render_template('login.html', ref=ref, login_failed=login_failed)


@admin.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return 'success'


def main():
    setup_daemon_logging(
        'admin',
        conf.app['file'] if os.path.isabs(conf.app['file']) else os.path.join(PROG_DIR, conf.app['file']),
        conf.app['debug']
    )

    admin.secret_key = os.urandom(24)
    admin.config['DEBUG'] = conf.app['debug']
    admin.config['SESSION_COOKIE_NAME'] = 'session'
    admin.config['JSONIFY_PRETTYPRINT_REGULAR'] = conf.app['debug']
    admin.config['PROPAGATE_EXCEPTIONS'] = True

    from gevent.pywsgi import WSGIServer
    from gevent import monkey
    monkey.patch_all(Event=True, dns=False)

    server = WSGIServer(
        ('', conf.app['port'] + 1), admin, log='default' if conf.app['debug'] else None, backlog=1024
    )
    server.serve_forever()


if __name__ == '__main__':
    os.chdir(PROG_DIR)
    main()
