# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import urlparse

import requests
from gevent.lock import Semaphore
from flask import Flask, request, Response, render_template
from functools import wraps

PROG_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import conf
except ImportError:
    import shutil

    shutil.copyfile('%s/conf.sample' % PROG_DIR, '%s/conf.py' % PROG_DIR)
    import conf

from comm.logger import setup_daemon_logging
from comm.db import db

app = Flask('app', static_folder='static', template_folder='static')
logger = None

accesstoken = None
a_expire_time = None


def expire_accesstoken(get_token):
    lock = Semaphore()

    @wraps(get_token)
    def decorator():
        global accesstoken
        global a_expire_time

        for i in range(2):
            data = None
            try:
                lock.acquire(timeout=30)
                if not accesstoken or time.time() > a_expire_time:
                    data = get_token()
                    accesstoken = data['access_token']
                    a_expire_time = time.time() + data['expires_in'] - 30
                    return {'access_token': accesstoken}
                else:
                    return {'access_token': accesstoken}
            except:
                logger.error('get acctoken failed: %s' % data, exc_info=True)
            finally:
                lock.release()
        else:
            return {'access_token': accesstoken}

    return decorator


@expire_accesstoken
def get_accesstoken():
    req = requests.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (
        conf.app['CorpID'], conf.app['Secret']))
    return req.json()


jsapiticket = None
j_expire_time = None


def expire_jsapiticket(get_token):
    lock = Semaphore()

    @wraps(get_token)
    def decorator():
        global jsapiticket
        global j_expire_time

        for i in range(2):
            data = None
            try:
                lock.acquire(timeout=30)
                if not jsapiticket or time.time() > j_expire_time:
                    data = get_token()
                    jsapiticket = data['ticket']
                    j_expire_time = time.time() + data['expires_in'] - 30
                    return {'ticket': jsapiticket}
                else:
                    return {'ticket': jsapiticket}
            except:
                logger.error('get jsticket failed: %s' % data, exc_info=True)
            finally:
                lock.release()
        else:
            return {'ticket': jsapiticket}

    return decorator


@expire_jsapiticket
def get_jsapiticket():
    req = requests.get(
        'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=%s' % get_accesstoken()['access_token'])
    return req.json()


url_map = {
    'AlumniCard': 'AlumniCard/AlumniCard.html',  # 校友卡
    'NearbyShop': 'NearbyShop/NearbyShop.html',  # 附近校企
    'NearbyCollege': 'NearbyCollege/NearbyCollege.html',  # 附近校友
    'AlumniCircle': 'Alumni_circle/activity_circle.html',  # 活动圈子
    'AlumniEndowment': 'AlumniEndowment/endowment.html',  # 校友捐赠
    'AlumnusMeeting': 'AlumnusMeeting/AlumnusMeeting.html',  # 联系校友会
    'ChenggeQuotation': 'ChenggeQuotation/cg-quotations.html',  # 诚哥语录
}

server_domain = urlparse.urlparse(conf.app['base_url']).hostname


@app.route('/commited')
def commited():
    import subprocess
    subprocess.call('git pull', shell=True)
    return 'ok'


@app.route('/')
def index():
    userid = request.cookies.get('userid')
    code = request.args.get('code')
    url = request.args.get('state')
    if not userid and not code and not url:
        return render_template('sorry.html')
    if not userid:
        req = requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=%s&code=%s' %
            (get_accesstoken()['access_token'], code)
        )
        data = req.json()
        if 'UserId' in data:
            # 企业用户访问
            weuserid = data['UserId']
            req = requests.post(
                'https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_openid?access_token=%s' %
                get_accesstoken()['access_token'],
                data=json.dumps({'userid': weuserid})
            )
            data = req.json()
            if 'openid' in data:
                openid = data['openid']
            else:
                logger.error('bad request openid: %s' % data)
                return render_template('500.html')
            user = db.user.find_one({'OpenId': openid})
            if user:
                userid = str(user['_id'])
            else:
                rv = db.user.insert_one({
                    'OpenId': openid,
                    'UserId': weuserid,
                })
                userid = str(rv.inserted_id)

        elif 'OpenId' in data:
            # 普通用户访问
            openid = data['OpenId']
            user = db.user.find_one({'OpenId': openid})
            if user:
                userid = str(user['_id'])
            else:
                rv = db.user.insert_one({
                    'OpenId': openid,
                })
                userid = str(rv.inserted_id)

        elif data.get('errcode') == 40029:
            # 用户重复刷新页面,忽略
            pass

        else:
            logger.error('bad request getuser: %s' % data)
            return render_template('500.html')

    res = Response()
    if userid:
        res.set_cookie('userid', str(userid), max_age=86400, httponly=False, secure=True, domain=server_domain)
    res.set_cookie(
        'jsticket', get_jsapiticket()['ticket'], max_age=86400, httponly=False, secure=True, domain=server_domain
    )

    if url in url_map:
        res.data = render_template(url_map[url])
    else:
        res.data = render_template('index.html')
    return res


def main():
    global logger
    logger = setup_daemon_logging(
        'app',
        conf.app['file'] if os.path.isabs(conf.app['file']) else os.path.join(PROG_DIR, conf.app['file']),
        conf.app['debug']
    )

    app.config['DEBUG'] = conf.app['debug']
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = conf.app['debug']
    app.config['PROPAGATE_EXCEPTIONS'] = True

    import re

    api_file_list = os.listdir(os.path.join(PROG_DIR, 'api/resources'))
    api_files = [
        re.search('^([^_]+.*)\.py$', i).groups()[0] for i in api_file_list if
        re.search('^([^_]+.*)\.py$', i)
        ]
    __import__('api.resources', fromlist=api_files)

    for rc in api_files:
        mount = getattr(sys.modules['api.resources.%s' % rc], '__mount__', None)
        if mount:
            mount()

    from api.wrappers import api
    api.init_app(app)

    from gevent import monkey
    from gevent.pywsgi import WSGIServer
    monkey.patch_all(Event=True, dns=False)

    server = WSGIServer(
        ('', conf.app['port']), app, log='default' if conf.app['debug'] else None, backlog=1024
    )
    server.serve_forever()


if __name__ == '__main__':
    os.chdir(PROG_DIR)
    main()
elif getattr(sys, 'ps1', None):
    import logging

    logging.basicConfig()
    logger = logging.getLogger('app')
else:
    import logging

    logger = logging.getLogger('app')
