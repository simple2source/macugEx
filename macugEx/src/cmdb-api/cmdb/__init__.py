from tornado.web import Application
from kazoo.client import KazooClient
from tornado.options import options, define

define('port', default=8000, type=int, help='server port')
define('bind', default='0.0.0.0', type=str, help='server bind')
define('connect', default='127.0.0.1:2181', type=str, help='zookeeper connect')
define('root', default='/cmdb/lock', type=str, help='zookeeper root')
define('es', default='http://127.0.0.1:9200', type=str, help='elasticsearch base url')
define('shards', default=1, type=int, help='number of index shards')
define('replicas', default=0, type=int, help='number of index replicas')


def make_app(router, **settings):
    app = Application(router, **settings)
    zk = KazooClient(hosts=options.connect)
    setattr(app, 'zk', zk)
    return app