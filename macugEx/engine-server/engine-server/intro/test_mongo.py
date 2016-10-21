import pymongo
import os


try:
    import conf
except ImportError:
    import sys

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    import conf


if __name__ == '__main__':
    if conf.mongo.get('username') and conf.mongo.get('password'):
        uri = 'mongodb://%s:%s@%s:%s' % (
            conf.mongo['username'], conf.mongo['password'], conf.mongo['host'], conf.mongo['port'])
    else:
        uri = 'mongodb://%s:%s' % (conf.mongo['host'], conf.mongo['port'])

    try:
        db = pymongo.MongoClient(uri, connect=True)
        db.server_info()
        print('connect success')
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
