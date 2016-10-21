# -*- coding: utf-8 -*-
from flask import Blueprint, request, session, render_template, abort, make_response, jsonify
from functools import wraps, partial
from bson.objectid import ObjectId, InvalidId
from bson.binary import Binary
from pymongo.helpers import DuplicateKeyError
from binascii import b2a_hex
from PIL import Image
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
from copy import deepcopy
import datetime
import calendar
import decimal
import tarfile
import zipfile
import types
import time
import json
import io
import re
import os
import setting

from core.db import db, redis, version_file, appstore_image, \
    bluetooth_file, banner_image, answer_game_image
from agent.client import Demand
from agent.alphabet import OK
from static.define import static_uri
from static.tools import plaza_image_delete, story_image_delete, story_audio_delete, story_content_delete
from tools import create_admin, make_story_content, create_story_document, decode_chinese

app = Blueprint('admin', __name__, url_prefix='/admin', static_folder='static')
agent = Demand(setting.broker['host'], setting.broker['request_port'])


def validate_permission(*permissions):
    """
    验证用户session中 permissions 参数中的权限是否符合设置的 permissions
    permissions 中:
        'all' 允许所有权限通过
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_permissions = request.permissions
            if user_permissions:
                for p in permissions:
                    if p == 'all' or p in user_permissions or 'admin' in user_permissions:
                        return func(*args, **kwargs)
            return abort(403)

        return wrapper

    return decorator


menubar = list(db.menubar.find())


@app.route('/', methods=['GET', 'PUT'])
@validate_permission('all')
def inedx():
    user_permissions = request.permissions
    if request.method == 'GET':
        user_menubar = []
        for m in menubar:
            if 'admin' in user_permissions or (set(m['permissions']) & set(user_permissions)):
                um = deepcopy(m)
                for sub_m_id, sub_m in um['submenubar'].items():
                    if 'admin' in user_permissions or (set(sub_m['permissions']) & set(user_permissions)):
                        continue
                    else:
                        del um['submenubar'][sub_m_id]
                user_menubar.append(um)
        return render_template('admin.html', menubar=user_menubar, username=session['nickname'], server_uri=static_uri)
    elif request.method == 'PUT':
        if request.data == 'permissions':
            return json.dumps(user_permissions)
    else:
        return abort(405)


def bson_binary_convert(obj):
    if hasattr(obj, 'iteritems'):
        return {k: bson_binary_convert(v) for k, v in obj.iteritems()}
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, unicode)):
        return list((bson_binary_convert(v) for v in obj))
    return b2a_hex(obj) if isinstance(obj, Binary) else obj


def custom_dumps_fix(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime.datetime):
        if obj.year < 1900:
            return '00-00-00 00:00:00'
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, datetime.date):
        if obj.year < 1900:
            return '00-00-00'
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, datetime.time):
        return obj.strftime('%H:%M')
    if isinstance(obj, decimal.Decimal):
        return "%.2f" % obj
    raise TypeError(repr(obj) + ' is not JSON serializable')


dumps = partial(json.dumps, default=custom_dumps_fix)


def year_to_datetime(year):
    return datetime.datetime.strptime(str(year), '%Y')


def str_to_ObjectId(str24):
    return ObjectId(str24)


types.YearType = year_to_datetime
types.ObjectIdType = str_to_ObjectId


def custom_loads_fix(obj):
    if '__type__' in obj:
        obj_type = getattr(types, obj['__type__'], None)
        if obj_type:
            return obj_type(obj['__value__'])
    return obj


loads = partial(json.loads, object_hook=custom_loads_fix)

collections = (
    'watch', 'user', 'group', 'message', 'story', 'appstore.category', 'banner', 'watch_locate', 'user_locate',
    'user_locus', 'devicetoken', 'watch_loger', 'watch_locus', 'admin', 'version', 'plaza', 'submail', 'answer_game',
    'answer_game.category', 'service')


def parse_request_params(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if request.mimetype == 'application/json':
            request_params = loads(request.data)
        elif request.form:
            p = {}
            for k, v in request.form.items():
                if v:
                    p[k] = loads(v)
            request_params = p
        elif request.args:
            p = {}
            for k, v in request.args.items():
                if v:
                    p[k] = loads(v)
            request_params = p
        elif request.data:
            request_params = loads(request.data)
        else:
            request_params = {}
        request.params = request_params
        return func(*args, **kwargs)

    return decorator


@app.route('/<collection>', methods=['GET', 'POST'])
@validate_permission('all')
@parse_request_params
def collection_handle(collection):
    if collection in collections:
        if request.method == 'GET':
            page = int(request.params.get('page', 0))
            num = int(request.params.get('num', 10))
            num = num if num <= 1000 else 1000
            find = request.params['find']
            fields = {f: 1 for f in request.params.get('field', [])}
            if 'sort' in request.params:
                sort = request.params['sort']
            else:
                sort = ('_id', -1)
            if fields:
                datas = list(db[collection].find(find, fields).sort(*sort).limit(num).skip(page * num))
            else:
                datas = list(db[collection].find(find).sort(*sort).limit(num).skip(page * num))
            if collection == 'watch_loger':
                return dumps(bson_binary_convert(datas))
            else:
                return dumps(datas)
        elif request.method == 'POST':
            ok = 0
            if collection == 'appstore.category' and 'category_manage' in request.permissions:
                ok = 1
            elif 'admin' in request.permissions:
                ok = 1
            if ok == 1:
                db[collection].update_many(request.params['find'], request.params['update'])
            return 'success'
    return abort(404)


@app.route('/<collection>/<handle>', methods=['GET'])
@validate_permission('all')
def collection_handleing(collection, handle):
    if collection not in collections:
        return abort(404)
    if handle == 'count':
        return str(db[collection].find(loads(request.args['find'])).count())
    elif handle == 'aggregate':
        return dumps(list(db[collection].aggregate(loads(request.args['pipeline']))))
    else:
        return abort(403)


@app.route('/watch/getlist', methods=['GET'])
@validate_permission('debug')
def watch_getlist():
    imei = request.args.get('imei')
    if imei:
        if agent.find(imei) == OK:
            return '["%s"]' % imei
        else:
            return '[]'
    else:
        imei_list = agent.getlist(request.args.get('page', 0), request.args.get('num', 10))
        return dumps(imei_list)


@app.route('/watch/gettotal', methods=['GET'])
@validate_permission('debug')
def watch_gettotal():
    return str(agent.gettotal())


@app.route('/story/compress/upload', methods=['POST'])
@validate_permission('story_manage')
def story_compress_upload():
    try:
        brief = request.form.get('brief')
        if not brief:
            brief = ''
        input_title = request.form.get('title')

        category_id = request.form.get('category_id', None)
        if category_id:
            category = db.appstore.category.find_one({'_id': category_id}, {'_id': 1})
            if not category:
                return 'category id not find'

        compress = request.files.get('compress')
        if not compress:
            return 'not compress file exists'
        amr = None
        mp3 = None
        jpg_raw_dicts = {}
        txt = None
        front_jpg = None
        title = None
        try:
            zfile = zipfile.ZipFile(compress)
            iter_method = zfile.namelist
            read_method = zfile.read
        except zipfile.BadZipfile:
            compress.seek(0)
            try:
                zfile = tarfile.open(fileobj=compress)
                iter_method = zfile.getnames
                read_method = lambda x: zfile.extractfile(x).read()
            except tarfile.TarError:
                return 'unknown compress file'

        for name in iter_method():
            filename = os.path.split(name)[-1:]
            if filename:
                filename = filename[0]
            if filename.startswith('.'):
                continue
            r = re.search(r'.*\.amr$', name)
            if r:
                # amr语音文件
                amr = read_method(name)
                continue
            r = re.search(r'.*\.mp3$', name)
            if r:
                # mp3语音文件
                mp3 = read_method(name)
                continue
            r = re.search(r'.*img.(\d)\.jpg$', name)
            if r:
                # 索引图片
                index = int(r.groups()[0])
                jpg_raw_dicts[index] = read_method(name)
                continue
            r = re.search(r'.*\.txt$', name)
            if r:
                # 索引文件
                txt = read_method(name)
                txt = decode_chinese(txt)
                if not txt:
                    return 'txt file decode Error, must be utf-8'
                continue
            r = re.search(r'.*\.jpg$', name)
            if r:
                # 封面图片
                front_jpg = read_method(name)
                if not input_title:
                    title = os.path.splitext(filename)[0]
                    title = decode_chinese(title)
                    if not title:
                        return 'title decode Error, must be utf-8'
                else:
                    title = input_title
                continue

        if not amr and not mp3:
            return 'miss .amr or .mp3 file'
        elif not jpg_raw_dicts:
            return 'miss /img/*.jpg file'
        elif not txt:
            return 'miss .txt or file empty'
        elif not front_jpg:
            return 'miss .jpg in root directory'
        elif not title:
            return 'miss .jpg in root directory'

        # jpg图片最大大小
        JPG_MAX_SIZE = 20480

        # f_240 符合腕表要求的封面图片
        if len(front_jpg) > JPG_MAX_SIZE:
            # 处理故事图片质量jpeg,240x240,quality=30
            frontcover = io.BytesIO(front_jpg)
            with Image.open(frontcover) as img:
                frontcover_240_240 = img.resize((240, 240), Image.ANTIALIAS)
            f_240 = io.BytesIO()
            frontcover_240_240.save(f_240, format='JPEG', quality=70)
            frontcover_240_240.close()

            f_240.seek(0)
        else:
            frontcover = io.BytesIO(front_jpg)
            f_240 = io.BytesIO(front_jpg)

        indexs = jpg_raw_dicts.keys()
        indexs.sort()  # [1,2,3,4]

        # 未处理的索引图片
        image_list = []
        # 符合腕表要求的索引图片
        image_list_240 = []

        for i in indexs:
            if i < 1:
                return '/img/*.jpg must start with 1, eg: 1.jpg, 2.jpg, 3.jpg'
            raw = jpg_raw_dicts[i]
            image_list.append(raw)
            if len(raw) > JPG_MAX_SIZE:
                with io.BytesIO(raw) as f:
                    with Image.open(f) as img:
                        img_240_240 = img.resize((240, 240), Image.ANTIALIAS)
                img_240_240_f = io.BytesIO()
                img_240_240.save(img_240_240_f, format='JPEG', quality=70)
                img_240_240.close()

                img_240_240_f.seek(0)
            else:
                img_240_240_f = io.BytesIO(raw)
            image_list_240.append(img_240_240_f)

        index_list = []
        time_list = []
        text_list = []
        for line, text in enumerate(txt.splitlines()):
            if not text:
                continue
            i, t, tt = text.split(',', 2)
            try:
                i = int(i) - 1
            except ValueError:
                return 'txt file index must is number(%d line)' % (line + 1)
            try:
                t = int(t)
            except ValueError:
                return 'txt file time must is number(%d line)' % (line + 1)
            index_list.append(i)
            time_list.append(t)
            text_list.append(tt)

        if mp3:
            audio = mp3
            audio_type = 'mp3'
        elif amr:
            audio = amr
            audio_type = 'amr'
        else:
            return 'bad audio file format'

        # 打包故事内容
        content = make_story_content(f_240, title, index_list, time_list, text_list, image_list_240, audio_type, audio)
        f_240.close()
        for i in image_list_240:
            i.close()
        # 重置文件对象指针
        frontcover.seek(0)
        # 开始创建故事
        create_story_document(title, brief, category_id, frontcover, image_list, index_list, time_list, text_list,
                              audio_type, audio, content)
        frontcover.close()
        return 'success'
    except Exception as e:
        return repr(e)


@app.route('/version/upload', methods=['POST'])
@validate_permission('version_manage')
def version_upload():
    number = request.form.get('number')
    if not number:
        return 'not version number exist'
    try:
        number = int(number)
    except ValueError:
        return 'version number is bad int type'
    name = request.form.get('name')
    if not name:
        return 'not name exist'
    platform = request.form.get('platform')
    if not platform:
        return 'not platform exist'
    log = request.form.get('log')
    if not log:
        return 'not log text exist'
    file = request.files.get('file')
    if not file:
        return 'not file exist'
    file_data = file.read()
    if not file_data:
        return 'file is empty'
    android_file_id = version_file.put(file_data)
    version = {
        'number': number,
        'name': name,
        'platform': platform,
        'log': log,
        'file_id': android_file_id,
        'maketime': datetime.datetime.now(),
    }
    db.version.insert(version)
    return 'success'


@app.route('/version/delete', methods=['POST'])
@validate_permission('version_manage')
@parse_request_params
def version_delete():
    number = request.params.get('number')
    if not number:
        return 'not version number exist'
    try:
        number = int(number)
    except ValueError:
        return 'version number is bad int type'
    version = db.version.find_one({'number': number})
    if version:
        if 'file_id' in version:
            version_file.delete(version['file_id'])
        db.version.delete_one({'number': number})
    return 'success'


@app.route('/story/delete', methods=['POST'])
@validate_permission('story_manage')
@parse_request_params
def story_delete():
    find = request.params['find']
    story_list = list(db.story.find(find))
    for story in story_list:
        if 'image_id' in story:
            story_image_delete(story['image_id'])
        if 'images' in story:
            for img_id in story['images']:
                story_image_delete(img_id)
        if 'audio_id' in story:
            story_audio_delete(story['audio_id'])
        if 'content_id' in story:
            story_content_delete(story['content_id'])
        if 'category_id' in story:
            hot_category = 'HotCategory:%s' % story['category_id']
            redis.zrem(hot_category, str(story['_id']))
    if len(story_list) > 0:
        db.story.delete_many(find)
    return 'success'


@app.route('/appstore.category.image/upload', methods=['POST'])
@validate_permission('category_manage')
def appstore_category_image_upload():
    category_id = request.form.get('category_id')
    if not category_id:
        return 'not category_id exists'
    image_name = request.form.get('image_name')
    if image_name not in ('image_id', 'image_id2'):
        return 'not image_id ot image_id2 exists'
    image = request.files.get('image')
    image_data = image.read()
    if not image_data:
        return 'image is empty'
    category = db.appstore.category.find_one({'_id': category_id})
    if not category:
        return 'category id error'
    if image_name in category:
        appstore_image.delete(category[image_name])
    image_id = appstore_image.put(image_data)
    db.appstore.category.update_one({'_id': category_id}, {'$set': {image_name: image_id}})
    return 'success'


@app.route('/appstore.category/upload', methods=['POST'])
@validate_permission('category_manage')
def appstore_category_upload():
    category_id = request.form.get('id')
    if not category_id:
        return 'not category_id exists'
    finding = db.appstore.category.find_one({'_id': category_id}, {'_id': 1})
    if finding:
        return '%s already exists' % category_id
    name = request.form.get('name')
    if not name:
        return 'not name exists'
    image1 = request.files.get('image1')
    if not image1:
        return 'image1 is empty'
    image2 = request.files.get('image2')
    if not image2:
        return 'image2 is empty'
    image_id1 = appstore_image.put(image1.read())
    image_id2 = appstore_image.put(image2.read())
    db.appstore.category.insert_one({
        '_id': category_id,
        'name': name,
        'image_id': image_id1,
        'image_id2': image_id2,
    })
    return 'success'


@app.route('/appstore.category/delete', methods=['POST'])
@validate_permission('category_manage')
@parse_request_params
def appstore_category_delete():
    category_id = request.params.get('category_id')
    if not category_id:
        return 'category id not exist'
    category = db.appstore.category.find_one({'_id': category_id})
    if category:
        if 'image_id' in category:
            appstore_image.delete(category['image_id'])
        if 'image_id2' in category:
            appstore_image.delete(category['image_id2'])
        db.appstore.category.delete_one({'_id': category_id})
    return 'success'


@app.route('/profile', methods=['GET', 'POST'])
@validate_permission('all')
@parse_request_params
def profile():
    username = session.get('username')
    if request.method == 'GET':
        user = db.admin.find_one({'_id': username}, {'password': 0})
        if not user:
            session.clear()
            return abort(403)
        return dumps(user)
    else:
        for limit in ('permissions', 'lasttime', 'maketime', '_id'):
            if limit in request.params:
                return abort(403)
        result = db.admin.update_one({'_id': username}, {'$set': request.params})
        if result.matched_count:
            if 'nickname' in request.params:
                session['nickname'] = request.params['nickname']
            return 'success'
        else:
            session.clear()
            return abort(403)


@app.route('/admin', methods=['GET', 'POST'])
@validate_permission('admin')
@parse_request_params
def admin():
    if request.method == 'GET':
        page = int(request.params.get('page', 0))
        num = int(request.params.get('num', 10))
        num = num if num <= 1000 else 1000
        find = request.params['find']
        fields = {f: 1 for f in request.params.get('field', [])}
        if 'sort' in request.params:
            sort = request.params['sort']
        else:
            sort = ('_id', -1)
        datas = list(db.admin.find(find, fields).sort(*sort).limit(num).skip(page * num))
        return dumps(datas)
    else:
        uid = request.params.get('_id')
        if not uid:
            return 'not _id exists'
        update = {}
        if request.params.get('nickname'):
            update['nickname'] = request.params['nickname']
        if request.params.get('permissions'):
            update['permissions'] = request.params['permissions']
        result = db.admin.update_one({'_id': uid}, {'$set': update})
        if result.matched_count:
            return 'success'
        else:
            return repr(result)


@app.route('/admin/create', methods=['POST'])
@validate_permission('admin')
@parse_request_params
def admin_create():
    uid = request.params.get('_id')
    if not uid:
        return 'not _id exists'
    nickname = request.params['nickname'] if request.params.get('nickname') else uid
    permissions = request.params.get('permissions')
    if not permissions:
        return 'permissions not exists'
    try:
        create_admin(uid, nickname, permissions)
    except DuplicateKeyError:
        return 'admin already exists'
    return 'success'


@app.route('/admin/delete', methods=['POST'])
@validate_permission('admin')
@parse_request_params
def admin_delete():
    uid = request.params.get('_id')
    if not uid:
        return 'not _id exists'
    db.admin.delete_one({'_id': uid})
    return 'success'


@app.route('/plaza/delete', methods=['POST'])
@validate_permission('plaza_manage')
@parse_request_params
def plaza_delete():
    find = request.params['find']
    plaza_list = list(db.plaza.find(find))
    for plaza in plaza_list:
        if 'images' in plaza:
            for image_id in plaza['images']:
                plaza_image_delete(image_id)
        db.plaza_like.delete_many({'_id': {'$regex': '^%s-' % plaza['_id']}})
        db.plaza_comment.delete_many({'post_id': str(plaza['_id'])})
    db.plaza.delete_many(find)
    return 'success'


@app.route('/watch/delete', methods=['POST'])
@validate_permission('watch_manage')
@parse_request_params
def watch_delete():
    find = request.params['find']
    watch_list = list(db.watch.find(find))
    for watch in watch_list:
        imei = watch['_id']
        group_id = redis.hget('Watch:%s' % imei, 'group_id')
        if group_id:
            now = time.time()
            db.group.update_one({'_id': int(group_id)}, {'$set': {
                'devs.%s.timestamp' % imei: now,
                'devs.%s.status' % imei: 0,
                'timestamp': now,
            }})
        redis.delete('Watch:%s' % imei)
        agent.send_nowait(imei, '\x0a', '')
        db.watch_jobbox.delete_many({'imei': imei})
        db.watch_locus.delete_many({'imei': imei})
        db.watch_locate.delete_many({'imei': imei})
    db.watch.delete_many(find)
    return 'success'


@app.route('/bluetooth/count', methods=['GET'])
@validate_permission('version_manage')
def bluetooth_count():
    return str(bluetooth_file.find().count())


@app.route('/bluetooth', methods=['GET'])
@validate_permission('version_manage')
def bluetooth():
    page = int(request.args.get('page', 0))
    num = int(request.args.get('num', 10))
    num = num if num <= 1000 else 1000
    datas = list(bluetooth_file.find().sort('uploadDate', -1).limit(num).skip(page * num))
    return dumps([{
                      '_id': i._id,
                      'version': i.version,
                      'maketime': datetime.datetime.fromtimestamp(calendar.timegm(i.upload_date.utctimetuple())),
                  }
                  for i in datas])


@app.route('/bluetooth/upload', methods=['POST'])
@validate_permission('version_manage')
def bluetooth_upload():
    number = request.form.get('version')
    if not number:
        return 'not version number exist'
    try:
        number = int(number)
    except ValueError:
        return 'version number is bad int type'
    file = request.files.get('file')
    if not file:
        return 'not file exist'
    file_data = file.read()
    if not file_data:
        return 'file is empty'
    bluetooth_file.put(file_data, version=number)
    return 'success'


@app.route('/bluetooth/delete', methods=['POST'])
@validate_permission('version_manage')
@parse_request_params
def bluetooth_delete():
    _id = request.params.get('_id')
    if not _id:
        return 'not id exist'
    try:
        _id = ObjectId(_id)
    except InvalidId:
        return 'id is bad ObjectId type'
    bluetooth_file.delete(_id)
    return 'success'


@app.route('/banner/upload', methods=['POST'])
def banner_upload():
    file = request.files.get('file')
    if not file:
        return 'not file exist'
    file_data = file.read()
    if not file_data:
        return 'file is empty'
    image_id = banner_image.put(file_data)
    db.banner.insert_one({'image_id': image_id})
    return 'success'


@app.route('/banner/delete', methods=['POST'])
@validate_permission('version_manage')
@parse_request_params
def banner_delete():
    _id = request.params.get('_id')
    if not _id:
        return 'not id exist'
    try:
        _id = ObjectId(_id)
    except InvalidId:
        return 'id is bad ObjectId type'
    banner = db.banner.find_one({'_id': _id})
    banner_image.delete(banner['image_id'])
    db.banner.delete_one({'_id': _id})
    return 'success'


@app.route('/answer_game/delete', methods=['POST'])
@validate_permission('game_manage')
@parse_request_params
def answer_game_delete():
    _id = request.params.get('_id')
    if not _id:
        return 'not id exist'
    try:
        _id = ObjectId(_id)
    except InvalidId:
        return 'id is bad ObjectId type'
    db.answer_game.delete_one({'_id': _id})
    return 'success'


@app.route('/answer_game/upload', methods=['POST'])
def answer_game_upload():
    question = request.form.get('question')
    if not question:
        return 'not question exist'
    answer = request.form.get('answer')
    if not answer:
        return 'not answer exist'
    try:
        option = int(request.form.get('option'))
    except (TypeError, ValueError):
        return 'option is bad int type'
    if option not in (1, 2):
        return 'option not is 1 or 2'
    category_id = request.form.get('category_id')
    if not category_id:
        return 'not category_id exist'
    db.answer_game.insert_one({
        'question': question,
        'answer': answer,
        'option': option,
        'category_id': category_id,
    })
    return 'success'


@app.route('/answer_game.category.image/upload', methods=['POST'])
@validate_permission('game_manage')
def answer_game_category_image_upload():
    category_id = request.form.get('category_id')
    if not category_id:
        return 'not category_id exists'
    image_name = request.form.get('image_name')
    if image_name != 'image_id':
        return 'not image_id exists'
    image = request.files.get('image')
    image_data = image.read()
    if not image_data:
        return 'image is empty'
    category = db.answer_game.category.find_one({'_id': category_id})
    if not category:
        return 'category id error'
    if image_name in category:
        answer_game_image.delete(category[image_name])
    image_id = answer_game_image.put(image_data)
    db.answer_game.category.update_one({'_id': category_id}, {'$set': {image_name: image_id}})
    return 'success'


@app.route('/answer_game.category/upload', methods=['POST'])
@validate_permission('game_manage')
def answer_game_category_upload():
    category_id = request.form.get('id')
    if not category_id:
        return 'not category_id exists'
    finding = db.answer_game.category.find_one({'_id': category_id}, {'_id': 1})
    if finding:
        return '%s already exists' % category_id
    name = request.form.get('name')
    if not name:
        return 'not name exists'
    image = request.files.get('image')
    if not image:
        return 'image is empty'
    image_id = answer_game_image.put(image.read())
    db.answer_game.category.insert_one({
        '_id': category_id,
        'name': name,
        'image_id': image_id,
    })
    return 'success'


@app.route('/answer_game.category/delete', methods=['POST'])
@validate_permission('game_manage')
@parse_request_params
def answer_game_category_delete():
    category_id = request.params.get('category_id')
    if not category_id:
        return 'category id not exist'
    category = db.answer_game.category.find_one({'_id': category_id})
    if category:
        if 'image_id' in category:
            answer_game_image.delete(category['image_id'])
        db.answer_game.category.delete_one({'_id': category_id})
    return 'success'


@app.route('/service/create', methods=['POST'])
@validate_permission('service_manage')
def service_create():
    username = request.form.get('username')
    if not username:
        return 'not username exist'
    password = request.form.get('password')
    if not username:
        return 'not password exist'
    try:
        db.service.insert({'_id': username, 'password': password, 'maketime': datetime.datetime.now()})
    except Exception as e:
        return repr(e)
    return 'success'


@app.route('/service/delete', methods=['POST'])
@validate_permission('service_manage')
@parse_request_params
def service_delete():
    find = request.params.get('find')
    if not find:
        return 'not query exist'
    db.service.delete_many(find)
    return 'success'


@app.route("/questions", methods=["GET", "POST"])
@validate_permission("service_manage")
@parse_request_params
def questions():
    if request.method == "GET":
        page = int(request.params.get("page", 0))
        num = int(request.params.get("num", 10))
        num = num if num <= 1000 else 1000
        find = request.params["find"]
        fields = {f: 1 for f in request.params.get("field", [])}
        if "sort" in request.params:
            sort = request.params["sort"]
        else:
            sort = ("_id", -1)
        if fields:
            datas = list(db.question.find(find, fields).sort(*sort).limit(num).skip(page * num))
        else:
            datas = list(db.question.find(find).sort(*sort).limit(num).skip(page * num))
        return dumps(datas)
    elif request.method == "POST":
        return make_response(jsonify({"message": "ok", "status": 200}))
    else:
        abort(405)


@app.route("/questions/count", methods=["GET"])
@validate_permission("service_manage")
def questions_count():
    return str(db.question.find(loads(request.args["find"])).count())


@app.route("/question/<string:question_id>", methods=["GET", "PUT", "DELETE"])
@validate_permission("service_manage")
@parse_request_params
def question(question_id):
    if request.method == "GET":
        return "success"
    elif request.method == 'PUT':
        return "success"
    elif request.method == 'DELETE':
        return "success"
    else:
        abort(405)


@app.route("/answers", methods=["GET"])
@validate_permission("service_manage")
@parse_request_params
def answers():
    if request.method == "GET":
        page = int(request.params.get("page", 0))
        num = int(request.params.get("num", 10))
        num = num if num <= 1000 else 1000
        find = request.params["find"]
        fields = {f: 1 for f in request.params.get("field", [])}
        if "sort" in request.params:
            sort = request.params['sort']
        else:
            sort = ("_id", -1)
        if fields:
            datas = list(db.serv_template_item.find(find, fields).sort(*sort).limit(num).skip(page * num))
        else:
            datas = list(db.serv_template_item.find(find).sort(*sort).limit(num).skip(page * num))
        return dumps(datas)


@app.route('/answer/create', methods=['POST'])
@validate_permission('service_manage')
def answer_create():
    if request.method == "POST":
        template_id = request.form.get("template_id")
        question = request.form.get("question")
        content = request.form.get("content")
        db.serv_template_item.insert_one({
            "template_id": template_id,
            "question": question,
            "content": content
        })
        return "success"
    else:
        abort(405)


@app.route("/answers/count", methods=["GET"])
@validate_permission("service_manage")
def answers_count():
    return str(db.serv_template_item.find(loads(request.args["find"])).count())


@app.route('/answer/delete', methods=['POST'])
@validate_permission('service_manage')
@parse_request_params
def answer_delete():
    find = request.params.get('find')
    if not find:
        return 'not query exist'
    db.serv_template_item.delete_one({u"_id": ObjectId(find[u"_id"])})
    return 'success'
