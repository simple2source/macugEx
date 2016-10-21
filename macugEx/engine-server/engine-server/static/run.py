# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_all(Event=True, dns=False)
from gevent.pywsgi import WSGIServer
import gevent
import ssl
import socket
import os
import io
import re
import time
import urllib
from functools import wraps
from flask import Flask, request, abort
from werkzeug.wrappers import Response
from datetime import datetime
from bson.objectid import ObjectId, InvalidId
from PIL import Image, ExifTags
import logging
from logging.handlers import RotatingFileHandler

for Orientation in ExifTags.TAGS.keys():
    if ExifTags.TAGS[Orientation] == 'Orientation':
        break

try:
    import ujson as json
except ImportError:
    import json

import sys

if sys.version_info.major < 3:
    range = xrange

sys.path.append('..')
from core.db import redis, message_image, message_audio, banner_image, appstore_image, version_file, bluetooth_file, \
    answer_game_image, Q_message_audio, Q_message_image
import conf
from tools import *

static = Flask('static')
use_nginx = conf.static['use_nginx']

# 头像模式中, normal级别,small级别的大小
normal_size = conf.static['normal_size']  # app端查看头像大小


def if_modified_since_handle(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if request.if_modified_since or request.if_none_match:
            headers = [('Content-Type', 'image/jpeg')]
            if request.if_modified_since:
                headers.append(('Last-Modified', request.if_modified_since.strftime('%a, %d %b %Y %H:%M:%S GMT')))
            if request.if_none_match:
                headers.append(('ETag', request.if_none_match))
            return Response(status=304, headers=headers)
        else:
            return func(*args, **kwargs)

    return decorator


def cache_image_in_path(cache_path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs['pattern'] not in ('small', 'normal', 'origin'):
                return abort(404)
            image_id = kwargs['filename'].split('.', 1)[0]
            image_path = cache_path % (image_id, kwargs['pattern'])
            if os.path.exists(image_path):
                image_time = datetime.fromtimestamp(os.stat(image_path).st_ctime)
                headers = [
                    ('Content-Type', 'image/jpeg'),
                    ('Last-Modified', image_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
                    ('ETag', image_id)
                ]
                if use_nginx:
                    headers.append(('X-Accel-Redirect', image_path[2:]))  # remove '..'
                    return Response(headers=headers)
                else:
                    return Response(open(image_path, 'rb').read(), headers=headers)
            else:
                return func(kwargs['pattern'], image_id)

        return wrapper

    return decorator


@static.route('/group/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
@cache_image_in_path('../cache/group/%s_%s.jpg')
def get_group_image(pattern, group_image_id):
    try:
        image_file = group_image_find(ObjectId(group_image_id))
    except InvalidId:
        return abort(404)
    if not image_file:
        return abort(404)
    image_path = image_pattern_thumbnail(image_file, pattern, '../cache/group/', group_image_id)
    headers = [
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', group_image_id)
    ]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/group/%s_%s.jpg' % (group_image_id, pattern)))
        response = Response(headers=headers)
    else:
        response = Response(open(image_path).read(), headers=headers)
    return response


@static.route('/user/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
@cache_image_in_path('../cache/user/%s_%s.jpg')
def get_user_image(pattern, user_image_id):
    try:
        image_file = user_image_find(ObjectId(user_image_id))
    except InvalidId:
        return abort(404)
    if not image_file:
        return abort(404)
    image_path = image_pattern_thumbnail(image_file, pattern, '../cache/user/', user_image_id)
    headers = [
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', user_image_id)
    ]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/user/%s_%s.jpg' % (user_image_id, pattern)))
        response = Response(headers=headers)
    else:
        response = Response(open(image_path).read(), headers=headers)
    return response


@static.route('/watch/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
@cache_image_in_path('../cache/watch/%s_%s.jpg')
def get_watch_image(pattern, watch_image_id):
    try:
        image_file = watch_image_find(ObjectId(watch_image_id))
    except InvalidId:
        return abort(404)
    if not image_file:
        return abort(404)
    image_path = image_pattern_thumbnail(image_file, pattern, '../cache/watch/', watch_image_id)
    headers = [
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', watch_image_id)
    ]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/watch/%s_%s.jpg' % (watch_image_id, pattern)))
        response = Response(headers=headers)
    else:
        response = Response(open(image_path).read(), headers=headers)
    return response


@static.route('/message/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
def get_message_image(pattern, filename):
    try:
        message_image_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    image_file = message_image.find_one(message_image_id)
    if not image_file:
        return abort(404)
    if pattern in ('normal', 'small'):
        img = Image.open(image_file)
        if hasattr(img, '_getexif'):
            exif = img._getexif()
            if exif:
                if exif[Orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[Orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[Orientation] == 8:
                    img = img.rotate(90, expand=True)
        img.thumbnail(normal_size, Image.ANTIALIAS)
        image_buff = io.BytesIO()
        # 默认保存jpeg时quality为75
        # subsampling为二次取样,默认开,降低缩略图的对比度,红色值多的图片效果明显
        # img.save(image_buff, format='JPEG', subsampling=1, quality=30)
        img.save(image_buff, format='JPEG', quality=70)
        image_buff.seek(0)
        image_data = image_buff.read()
    else:
        image_data = image_file.read()
    response = Response(headers=[
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(message_image_id))
    ])
    response.data = image_data
    return response


@static.route('/message/audio/<filename>', methods=['GET'])
@if_modified_since_handle
def get_message_audio(filename):
    try:
        message_audio_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    audio_file = message_audio.find_one(message_audio_id)
    if not audio_file:
        return abort(404)
    return Response(audio_file.read(), headers=[
        ('Content-Type', 'audio/amr'),
        ('Last-Modified', audio_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(message_audio_id))
    ])


@static.route('/question_message/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
def get_question_message_image(pattern, filename):
    try:
        message_image_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    image_file = Q_message_image.find_one(message_image_id)
    if not image_file:
        return abort(404)
    if pattern in ('normal', 'small'):
        img = Image.open(image_file)
        if hasattr(img, '_getexif'):
            exif = img._getexif()
            if exif:
                if exif[Orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[Orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[Orientation] == 8:
                    img = img.rotate(90, expand=True)
        img.thumbnail(normal_size, Image.ANTIALIAS)
        image_buff = io.BytesIO()
        # 默认保存jpeg时quality为75
        # subsampling为二次取样,默认开,降低缩略图的对比度,红色值多的图片效果明显
        # img.save(image_buff, format='JPEG', subsampling=1, quality=30)
        img.save(image_buff, format='JPEG', quality=70)
        image_buff.seek(0)
        image_data = image_buff.read()
    else:
        image_data = image_file.read()
    response = Response(headers=[
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(message_image_id))
    ])
    response.data = image_data
    return response


@static.route('/question_message/audio/<filename>', methods=['GET'])
@if_modified_since_handle
def get_question_message_audio(filename):
    try:
        message_audio_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    audio_file = Q_message_audio.find_one(message_audio_id)
    if not audio_file:
        return abort(404)
    return Response(audio_file.read(), headers=[
        ('Content-Type', 'audio/amr'),
        ('Last-Modified', audio_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(message_audio_id))
    ])


@static.route('/banner/image/<filename>', methods=['GET'])
@if_modified_since_handle
def get_banner_image(filename):
    try:
        banner_image_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    image_path = '../cache/banner/%s.jpg' % banner_image_id
    if os.path.exists(image_path):
        image_time = datetime.fromtimestamp(os.stat(image_path).st_ctime)
        return Response(open(image_path, 'rb').read(), headers=[
            ('Content-Type', 'image/jpeg'),
            ('Last-Modified', image_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('ETag', str(banner_image_id))
        ])
    image_file = banner_image.find_one(banner_image_id)
    if not image_file:
        return abort(404)
    image_data = image_file.read()
    if not image_data:
        return abort(404)
    with open(image_path, 'wb') as f:
        f.write(image_data)
    response = Response(headers=[
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(banner_image_id))
    ])
    response.data = image_data
    return response


@static.route('/category/image/<filename>', methods=['GET'])
@if_modified_since_handle
def get_category_image(filename):
    try:
        category_image_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    image_path = '../cache/category/%s.jpg' % category_image_id
    if os.path.exists(image_path):
        image_time = datetime.fromtimestamp(os.stat(image_path).st_ctime)
        return Response(open(image_path, 'rb').read(), headers=[
            ('Content-Type', 'image/jpeg'),
            ('Last-Modified', image_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('ETag', str(category_image_id))
        ])
    image_file = appstore_image.find_one(category_image_id)
    if not image_file:
        return abort(404)
    image_data = image_file.read()
    if not image_data:
        return abort(404)
    with open(image_path, 'wb') as f:
        f.write(image_data)
    response = Response(headers=[
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(category_image_id))
    ])
    response.data = image_data
    return response


@static.route('/game_category/image/<filename>', methods=['GET'])
@if_modified_since_handle
def get_game_category_image(filename):
    try:
        category_image_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    image_path = '../cache/category/%s.jpg' % category_image_id
    if os.path.exists(image_path):
        image_time = datetime.fromtimestamp(os.stat(image_path).st_ctime)
        return Response(open(image_path, 'rb').read(), headers=[
            ('Content-Type', 'image/jpeg'),
            ('Last-Modified', image_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('ETag', str(category_image_id))
        ])
    image_file = answer_game_image.find_one(category_image_id)
    if not image_file:
        return abort(404)
    image_data = image_file.read()
    if not image_data:
        return abort(404)
    with open(image_path, 'wb') as f:
        f.write(image_data)
    response = Response(headers=[
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(category_image_id))
    ])
    response.data = image_data
    return response


@static.route('/android/<filename>', methods=['GET'])
@if_modified_since_handle
def get_android_version_file(filename):
    try:
        android_file_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    file_path = '../cache/android/%s.apk' % android_file_id
    if not os.path.exists(file_path):
        android_file = version_file.find_one(android_file_id)
        if not android_file:
            return abort(404)
        android_data = android_file.read()
        with open(file_path, 'wb') as f:
            f.write(android_data)
        return Response(android_data, headers=[
            ('Content-Type', 'application/octet-stream')
        ])
    headers = [('Content-Type', 'application/octet-stream')]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/android/%s.apk' % android_file_id))
        response = Response(headers=headers)
    else:
        with open(file_path) as f:
            response = Response(f.read(), headers=headers)
    return response


@static.route('/plaza/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
@cache_image_in_path('../cache/plaza/%s_%s.jpg')
def get_plaza_image(pattern, post_image_id):
    try:
        image_file = plaza_image_find(ObjectId(post_image_id))
    except InvalidId:
        return abort(404)
    if not image_file:
        return abort(404)
    image_path = image_pattern_thumbnail(image_file, pattern, '../cache/plaza/', post_image_id)
    headers = [
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', post_image_id)
    ]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/plaza/%s_%s.jpg' % (post_image_id, pattern)))
        response = Response(headers=headers)
    else:
        with open(image_path) as f:
            response = Response(f.read(), headers=headers)
    return response


@static.route('/story/image/<pattern>/<filename>', methods=['GET'])
@if_modified_since_handle
@cache_image_in_path('../cache/story/%s_%s.jpg')
def get_story_image(pattern, story_image_id):
    try:
        image_file = story_image_find(ObjectId(story_image_id))
    except InvalidId:
        return abort(404)
    if not image_file:
        return abort(404)
    image_path = image_pattern_thumbnail(image_file, pattern, '../cache/story/', story_image_id)
    headers = [
        ('Content-Type', 'image/jpeg'),
        ('Last-Modified', image_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', story_image_id)
    ]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/story/%s_%s.jpg' % (story_image_id, pattern)))
        response = Response(headers=headers)
    else:
        with open(image_path) as f:
            response = Response(f.read(), headers=headers)
    return response


@static.route('/story/audio/<filename>', methods=['GET'])
@if_modified_since_handle
def get_story_audio(filename):
    try:
        story_audio_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    audio_path = '../cache/story/%s.amr' % story_audio_id
    if os.path.exists(audio_path):
        audio_time = datetime.fromtimestamp(os.stat(audio_path).st_ctime)
        return Response(open(audio_path, 'rb').read(), headers=[
            ('Content-Type', 'audio/amr'),
            ('Last-Modified', audio_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('ETag', str(story_audio_id))
        ])
    audio_file = story_audio_find(story_audio_id)
    if not audio_file:
        return abort(404)
    audio_data = audio_file.read()
    with open(audio_path, 'wb') as f:
        f.write(audio_data)
    return Response(audio_data, headers=[
        ('Content-Type', 'audio/amr'),
        ('Last-Modified', audio_file.upload_date.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(story_audio_id))
    ])


@static.route('/story/content/<filename>', methods=['GET'])
@if_modified_since_handle
def get_story_content(filename):
    try:
        story_content_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    content_path = '../cache/story/%s.data' % story_content_id
    if os.path.exists(content_path):
        content_file = open(content_path, 'rb')
        content_time = datetime.fromtimestamp(os.stat(content_path).st_ctime)
        file_exists = 1
    else:
        content_file = story_content_find(story_content_id)
        if not content_file:
            return abort(404)
        content_time = content_file.upload_date
        content_data = content_file.read()
        with open(content_path, 'wb') as f:
            f.write(content_data)
        file_exists = 0
    if request.range:
        if file_exists:
            content_file.seek(0, 2)
            content_length = content_file.tell()
        else:
            # content_file.seek(0, 2)
            # content_length = content_file.tell()
            # <gridfs.grid_file.GridOut> behavior most like <file>
            content_length = content_file.length
        # >>> print request.range, request_file_range
        # bytes=120000-129472 (120000, 129473)
        # bytes=120000-129473 (120000, 129473)
        # bytes=0-0           (0, 1)
        # bytes=0-            (0, 129473)
        # bytes=129472-129472 (129472, 129473)
        # bytes=129472-129473 (129472, 129473)
        # bytes=129473-129473 None
        # bytes=129473-129474 None
        request_file_range = request.range.range_for_length(content_length)
        if request_file_range:
            # 非 multipart/range 请求,响应一段文件分段,否则返回正常响应
            start, end = request_file_range
            if file_exists:
                content_file.seek(start)
                content_data = content_file.read(end - start)
            else:
                content_data = content_data[start:end]
            return Response(content_data, 206, headers=[
                ('Accept-Ranges', 'bytes'),
                ('Content-Range', 'bytes %s-%s/%s' % (start, end - 1, content_length)),
                ('Content-Type', 'application/octet-stream'),
            ])
        else:
            return abort(416)
    if file_exists:
        # if request.range get content_length will seek(0, 2)
        content_file.seek(0)
        content_data = content_file.read()
    return Response(content_data, headers=[
        ('Accept-Ranges', 'bytes'),
        ('Content-Type', 'application/octet-stream'),
        ('Last-Modified', content_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(story_content_id))
    ])


@static.route('/bluetooth/<filename>', methods=['GET'])
def get_bluetooth_content(filename):
    try:
        bluetooth_file_id = ObjectId(filename.split('.', 1)[0])
    except InvalidId:
        return abort(404)
    content_path = '../cache/bluetooth/%s.bin' % bluetooth_file_id
    if os.path.exists(content_path):
        content_file = open(content_path, 'rb')
        content_time = datetime.fromtimestamp(os.stat(content_path).st_ctime)
        file_exists = 1
    else:
        content_file = bluetooth_file.find_one(bluetooth_file_id)
        if not content_file:
            return abort(404)
        content_time = content_file.upload_date
        content_data = content_file.read()
        with open(content_path, 'wb') as f:
            f.write(content_data)
        file_exists = 0
    if request.range:
        if file_exists:
            content_file.seek(0, 2)
            content_length = content_file.tell()
        else:
            content_length = content_file.length
        request_file_range = request.range.range_for_length(content_length)
        if request_file_range:
            start, end = request_file_range
            if file_exists:
                content_file.seek(start)
                content_data = content_file.read(end - start)
            else:
                content_data = content_data[start:end]
            return Response(content_data, 206, headers=[
                ('Accept-Ranges', 'bytes'),
                ('Content-Range', 'bytes %s-%s/%s' % (start, end - 1, content_length)),
                ('Content-Type', 'application/octet-stream'),
            ])
        else:
            return abort(416)
    if file_exists:
        content_file.seek(0)
        content_data = content_file.read()
    return Response(content_data, headers=[
        ('Accept-Ranges', 'bytes'),
        ('Content-Type', 'application/octet-stream'),
        ('Last-Modified', content_time.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('ETag', str(bluetooth_file_id))
    ])


alp_filename = '../cache/current_almanac.alp'
if os.path.exists(alp_filename):
    alp_file_length = os.stat(alp_filename).st_size
else:
    alp_file_length = 0


@static.route('/almanac/current.alp', methods=['GET'])
def get_almanac():
    if request.range:
        alp_file_p = open(alp_filename, 'rb')
        request_file_range = request.range.range_for_length(alp_file_length)
        if request_file_range:
            start, end = request_file_range
            alp_file_p.seek(start)
            content_data = alp_file_p.read(end - start)
            return Response(content_data, 206, headers=[
                ('Accept-Ranges', 'bytes'),
                ('Content-Range', 'bytes %s-%s/%s' % (start, end - 1, alp_file_length)),
                ('Content-Type', 'application/octet-stream'),
            ])
        else:
            return abort(416)
    headers = [
        ('Content-Type', 'application/octet-stream'),
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Expires', '0'),
    ]
    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/current_almanac.alp'))
        response = Response(headers=headers)
    else:
        response = Response(open(alp_filename, 'rb').read(), headers=headers)
    return response


logger = logging.getLogger('static')
logfile = os.path.abspath(os.path.join(os.path.dirname(conf.__file__), conf.static['logfile']))
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(conf.static['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(conf.static['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


static.config['DEBUG'] = conf.static['debug']
static.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    default_image_handle()

    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    if conf.static['use_local']:
        from gevent import socket

        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists('./static.sock'):
            os.remove('./static.sock')
        listener.bind(os.path.join(os.path.abspath('./'), 'static.sock'))
        listener.listen(1024)
        server = WSGIServer(listener, static, log=None)
    else:
        server = WSGIServer(('', conf.static['use_port']), static, log=None, backlog=1024)
    server.serve_forever()
