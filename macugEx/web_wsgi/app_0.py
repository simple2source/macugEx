# -*- coding:utf-8 -*-
import os


def application(environ, start_response):
    for k, v in environ.items():
        if k not in os.environ:
            print('{} ==>{}'.format(k, v))
    start_response('200 ok', [('Content-Type', 'text/plain')])
    return ['hello'.encode()]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 9001, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
