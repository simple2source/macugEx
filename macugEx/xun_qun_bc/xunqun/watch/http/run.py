# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all(Event=True, dns=False)
from werkzeug.wrappers import Response
from gevent.pywsgi import WSGIServer
from bson.objectid import ObjectId
from server import WatchHttp
from qrcode.image.pil import PilImage
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from random import choice
import time
import io

try:
    import ujson as json
except ImportError:
    import json
try:
    import setting
except ImportError:
    import sys

    sys.path.append('../..')
    import setting

from core.db import db, redis, message_audio
from core.proxy import Client
from static.define import *
from static import define

push = Client(setting.push['host'], setting.push['port'])
app = WatchHttp()

BadArgs = Response(headers=[('Content-Type', 'text/html'), ('charset', 'utf-8')])
BadArgs.data = 'invalid parameter'

BadSess = Response(headers=[('Content-Type', 'text/html'), ('charset', 'utf-8')])
BadSess.data = 'unauthorized'


def response_dumps(d):
    data = json.dumps(d)
    response = Response(headers=[('Content-Type', 'application/json'), ('charset', 'utf-8')])
    response.data = data
    return response


def verify_imei_session(imei, session):
    if not imei or not session:
        return BadArgs


@app.route('info')
def info(request):
    session = request.args.get('session')
    imei = request.args.get('imei')
    err = verify_imei_session(imei, session)
    if err:
        return err
    group_id = redis.hget('Watch:%s' % imei, 'group_id')
    if group_id:
        group_id = int(group_id)
        group = db.group.find_one({'_id': group_id}, {'devs': 1})
        if 'devs' in group and imei in group['devs']:
            g_watch = group['devs'][imei]
            return response_dumps({'name': g_watch.get('name', ''), 'phone': g_watch.get('phone', '')})
    return response_dumps({'name': '', 'phone': ''})


@app.route('contactbook')
def contactbook(request):
    session = request.args.get('session')
    imei = request.args.get('imei')
    if not request.args.get('timestamp'):
        return BadArgs
    try:
        timestamp = float(request.args['timestamp'])
    except ValueError:
        return BadArgs
    err = verify_imei_session(imei, session)
    if err:
        return err
    contacts = {}
    group_id, customer_id = redis.hmget('Watch:%s' % imei, 'group_id', 'customer_id')
    if group_id:
        app_ident = define.config_customer.get(int(customer_id), 'default') if customer_id else 'default'
        group = db.group.find_one({'_id': int(group_id)}, {'users': 1, 'contacts': 1, 'timestamp': 1})
        if group.get('timestamp') > timestamp:
            user_search_list = []
            for user_id, g_user in group.get('users', {}).items():
                if g_user.get('timestamp') > timestamp:
                    uid = ObjectId(user_id)
                    if g_user.get('status'):
                        user_search_list.append(uid)
                    contacts[uid] = {
                        'id': user_id,
                        'name': g_user.get('name', u'未填'),
                        'phone': g_user.get('phone', ''),
                        'mac': '',
                        'portrait': user_image_small_path % g_user['image_id'] if 'image_id' in g_user else \
                            user_image_small_path_default % app_ident,
                        'status': g_user.get('status', 0),
                    }

            for user in db.user.find({'_id': {'$in': user_search_list}}, {'mac': 1}):
                contacts[user['_id']]['mac'] = user.get('mac', '')

            contacts = contacts.values()
            for phone, contact in group.get('contacts', {}).items():
                if contact.get('timestamp') > timestamp:
                    contacts.append({
                        'id': phone,
                        'name': contact.get('name', u'未填'),
                        'phone': phone,
                        'mac': '',
                        'portrait': contact_image_small_path_default % app_ident,
                        'status': contact.get('status', 0),
                    })
            timestamp = group['timestamp']
    else:
        timestamp = 0
    return response_dumps({'timestamp': timestamp, 'contacts': contacts})


@app.route('sendaudio')
def sendaudio(request):
    session = request.form.get('session')
    imei = request.form.get('imei')
    err = verify_imei_session(imei, session)
    if err:
        return err
    if not request.files.get('audio') or not request.form.get('length'):
        return BadArgs
    group_id = redis.hget('Watch:%s' % imei, 'group_id')
    if not group_id:
        response = Response()
        response.data = 'failed'
        return response
    else:
        group_id = int(group_id)
    try:
        length = int(request.form['length'])
    except ValueError:
        return BadArgs
    content_id = message_audio.put(request.files['audio'].read())
    now = time.time()
    message_id = db.message.insert_one({
        'group_id': group_id,
        'type': 1,
        'content': content_id,
        'length': length,
        'sender': imei,
        'sender_type': 2,
        'timestamp': now
    }).inserted_id
    push(1, group_id, {
        'push_type': 'talk',
        'group_id': group_id,
        'sender': imei,
        'sender_type': 2,
        'message_id': str(message_id),
        'type': 1,
        'content': message_audio_path % content_id,
        'length': length,
        'timestamp': now
    })
    response = Response()
    response.data = 'succed'
    return response


@app.route('activeme')
def info(request):
    if not request.args.get('customer_id'):
        return BadArgs
    session = request.args.get('session')
    imei = request.args.get('imei')
    err = verify_imei_session(imei, session)
    if err:
        return err
    try:
        customer_id = int(request.args['customer_id'])
    except ValueError:
        return BadArgs

    auth = ''.join([choice(chars) for _ in range(6)])
    redis.setex('WatchToken:%s:%s' % (imei, auth), 900, 1)

    qr = QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=5,
        border=1,
        image_factory=PilImage,
    )
    qr.add_data('http://fir.im/xq02?imei=%s&authcode=%s&customer_id=%s&ttl=%s' % (
        imei, auth, customer_id, time.time() + 900))
    img = qr.make_image()
    f = io.BytesIO()
    img.save(f, 'JPEG')
    response = Response(headers=[('Content-Type', 'image/jpeg')])
    response.data = f.getvalue()
    f.close()
    return response


if __name__ == '__main__':
    server = WSGIServer(('', setting.server['http_port']), app, log=None, backlog=1024)
    server.serve_forever()
