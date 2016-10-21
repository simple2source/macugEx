# -*- coding: utf-8 -*-
from gevent.pywsgi import WSGIServer
from werkzeug.urls import url_decode
import os

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

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), './config.json'), 'r') as f:
    config = {int(k): v for k, v in json.loads(f.read()).items()}


def handle(environ, start_response):
    query = url_decode(environ.get('QUERY_STRING', ''))
    try:
        customer_id = int(query.get('customid', 0))
    except ValueError:
        customer_id = 0
    try:
        c = config[customer_id]
    except KeyError:
        c = config[0]
    start_response('200', [('Content-Type', 'application/json')])
    return json.dumps(c)


if __name__ == '__main__':
    server = WSGIServer(('', setting.server['conf_port']), handle, log=None, backlog=1024)
    server.serve_forever()
