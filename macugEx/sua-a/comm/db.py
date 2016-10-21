# -*- coding: utf-8 -*-
# 定义数据库连接
import pymongo

try:
    import conf
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import conf

__all__ = ['db']

if conf.mongodb.get('username') and conf.mongodb.get('password'):
    uri = 'mongodb://%s:%s@%s:%s' % (
        conf.mongodb['username'], conf.mongodb['password'], conf.mongodb['host'], conf.mongodb['port'])
else:
    uri = 'mongodb://%s:%s' % (conf.mongodb['host'], conf.mongodb['port'])

db = pymongo.MongoClient(uri, connect=False)[conf.mongodb['database']]


def create_indexs():
    db.user.create_index([
        ('OpenId', pymongo.ASCENDING),
    ])
    db.user.create_index([
        ('career', pymongo.ASCENDING),
    ])
    db.user.create_index([
        ('loc', '2dsphere'),
    ])
    db.user.create_index([
        ('donateNum', pymongo.ASCENDING),
    ])
    db.company.create_index([
        ('loc', '2dsphere'),
    ])
    db.donate.create_index([
        ('found_id', pymongo.ASCENDING),
    ])
    db.donate.create_index([
        ('user_id', pymongo.ASCENDING),
    ])


if __name__ == '__main__':
    create_indexs()
