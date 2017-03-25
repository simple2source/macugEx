# -*- coding:utf-8 -*-
import os
from cgi import parse
try:
    from urlparse import parse_qsl
except ImportError:
    # 3.5
    from urllib import parse_qsl


def application(environ, start_response):
    # environ is wsgiref get client env to input application args
    for k, v in environ.items():
        if k not in os.environ:
            print('{} ==>{}'.format(k, v))
    query_string = environ['QUERY_STRING']
    param = parse_qsl(query_string)
    print(param)
    # start_response to return header
    start_response('200 ok', [('Content-Type', 'text/plain')])
    # return to body
    return ['hello'.encode()]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 9001, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
