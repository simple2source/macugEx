# -*- coding: utf-8 -*-
from redis import ConnectionPool, StrictRedis
from time import time
import pymongo
from pymongo.errors import CollectionInvalid
import gridfs
import sys

try:
    import conf
except ImportError:
    sys.path.append('..')
    import conf

if conf.mongo.get('username') and conf.mongo.get('password'):
    uri = 'mongodb://%s:%s@%s:%s' % (
        conf.mongo['username'], conf.mongo['password'], conf.mongo['host'], conf.mongo['port'])
else:
    uri = 'mongodb://%s:%s' % (conf.mongo['host'], conf.mongo['port'])

db = pymongo.MongoClient(uri, connect=False)[conf.mongo['database']]


def dump_pending_task(imei, data):
    """
    :param imei: 设备imei
    :param data: 指令数据, eg: {'type':1, 'imei': ...}
    """
    db.watch_jobbox.insert_one({
        'imei': imei,
        'type': data['type'],
        'data': data,
        'timestamp': time(),
    })


class DB:
    db = db
    user_face = gridfs.GridFS(db, collection='user.face')
    message_audio = gridfs.GridFS(db, collection='message.audio')
    message_image = gridfs.GridFS(db, collection='message.image')
    banner_image = gridfs.GridFS(db, collection='banner.image')
    appstore_image = gridfs.GridFS(db, collection='appstore.category.image')
    version_file = gridfs.GridFS(db, collection='version.file')
    bluetooth_file = gridfs.GridFS(db, collection='watch.bluetooth.file')
    answer_game_image = gridfs.GridFS(db, collection='answer_game.category.image')
    Q_message_audio = gridfs.GridFS(db, collection='question_message.audio')
    Q_message_image = gridfs.GridFS(db, collection='question_message.image')
    dump_pending_task = dump_pending_task

    _redis = None

    @property
    def redis(self):
        if not self._redis:
            self._redis = StrictRedis(
                connection_pool=ConnectionPool(
                    host=conf.redis['host'], port=conf.redis['port'], password=conf.redis['password']
                )
            )
        return self._redis

    @property
    def __all__(self):
        return (
            'redis', 'db', 'user_face', 'message_audio', 'message_image',
            'dump_pending_task', 'banner_image', 'appstore_image', 'version_file', 'bluetooth_file',
            'answer_game_image', 'Q_message_audio', 'Q_message_image'
        )


def create_index():
    # 用户session
    db.user.create_index([('session', pymongo.ASCENDING)])
    # 腕表mac地址
    db.watch.create_index([('mac', pymongo.ASCENDING)])
    # 腕表指令日志
    try:
        db.create_collection('watch_loger', capped=True, size=629145600)
    except CollectionInvalid:
        db.command('convertToCapped', 'watch_loger', size=629145600)
    db.watch_loger.create_index([('imei', pymongo.ASCENDING)])
    # 腕表离线指令
    db.watch_jobbox.create_index([('imei', pymongo.ASCENDING)])
    # 索引排序值仅在使用复合索引查询,且查询时所指定排序方式与该索引排序值不同时影响大
    db.message.create_index([('group_id', pymongo.ASCENDING)])
    # 腕表定位
    db.watch_locate.create_index([('loc', '2dsphere')])
    db.watch_locate.create_index([('imei', pymongo.ASCENDING), ('timestamp', pymongo.ASCENDING)])
    # 腕表轨迹点
    db.watch_locus.create_index([('imei', pymongo.ASCENDING), ('timestamp', pymongo.ASCENDING)])
    # 用户定位
    db.user_locate.create_index([('loc', '2dsphere')])
    db.user_locate.create_index([('user_id', pymongo.ASCENDING), ('timestamp', pymongo.ASCENDING)])
    # 用户轨迹点
    db.user_locus.create_index([('user_id', pymongo.ASCENDING), ('timestamp', pymongo.ASCENDING)])
    # TODO 圈子邮箱唯一
    # db.group.create_index([('email', pymongo.ASCENDING)], unique=True, sparse=True)
    # 故事
    db.story.create_index([('category_id', pymongo.ASCENDING)])
    # 广场消息点赞记录
    db.plaza_like.create_index([('timestamp', pymongo.ASCENDING)])
    # 广场消息评论记录
    db.plaza_comment.create_index([('post_id', pymongo.ASCENDING)])
    # APP安卓软件版本
    db.version.create_index([('number', pymongo.ASCENDING)])
    # submail反馈
    db.submail.create_index([('timestamp', pymongo.ASCENDING)])
    # 腕表定位调试日志
    try:
        db.create_collection('watch_gps_loger', capped=True, size=104857600)
    except CollectionInvalid:
        db.command('convertToCapped', 'watch_gps_loger', size=104857600)
    db.watch_gps_loger.create_index([('imei', pymongo.ASCENDING), ('timestamp', pymongo.ASCENDING)])
    # 腕表答题记录
    db.watch_answer_game.create_index([('imei', pymongo.ASCENDING), ('end_timestamp', pymongo.ASCENDING)])
    # 客服模块
    db.question.create_index([('user_id', pymongo.ASCENDING)])
    db.question.create_index([('status', pymongo.ASCENDING), ('serv_id', pymongo.ASCENDING)])
    db.question_message.create_index([('question_id', pymongo.ASCENDING)])
    # 客服回答模板
    db.serv_template_item.create_index([('template_id', pymongo.ASCENDING)])


    # 查找距离113.4395689,23.1658488坐标1000米范围的记录
    # db.watch_locate.find({
    #   'loc': {
    #       '$near': {
    #           '$geometry': {
    #               'type': "Point",
    #               'coordinates': [113.4395689,23.1658488]},
    #               '$maxDistance': 1000
    #           }
    #       }
    # })


if __name__ == '__main__':
    create_index()
else:
    sys.modules[__name__] = DB()

    # reimport to effect after sys.modules relaods
    import conf
    from redis import StrictRedis, ConnectionPool
