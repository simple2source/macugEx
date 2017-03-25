# -*- coding:utf-8 -*-

import webob
from functools import wraps
from webob.dec import wsgify


def application(environ, start_response):
    """version 1 use webob deal request and response"""
    # environ is wsgiref get client env to input application args
    # request
    request = webob.Request(environ)
    param = request.params
    body = request.body
    print(param, body)

    # start_response to return header
    # response
    response = webob.Response()
    response.body = 'hello {}'.format('webob')
    response.status_code = 200
    response.content_type = 'text/plain'
    return response(environ, start_response)


def webob_wsgify(app):
    @wraps(app)
    def wrap(environ, start_response):
        request = webob.Request(environ)
        response = app(request)
        return response(environ, start_response)
    return wrap


@wsgify
def application_v2(request):
    """version 2  use dec application"""
    # environ is wsgiref get client env to input application args
    # request
    param = request.params
    body = request.body
    print(param, body)

    # start_response to return header
    # response
    response = webob.Response()
    response.body = 'hello {}'.format('webob')
    response.status_code = 200
    response.content_type = 'text/plain'
    return response

# ---------- v3 basic route-------------->


@wsgify
def application_v3(request):
    """version 2 use difference path to basic route"""
    if request.path == '/hello':
        name = request.params.get('name', 'eve')
        response = webob.Response()
        response.text = 'hello {}'.format(name)
        response.status_code = 200
        response.content_type = 'text/plain'
        return response
    return webob.Response(body='use lar', content_type='text/plain')

# --------------v4 more deal route---------------------->


def hello(request):
    name = request.params.get('name', 'wlp')
    response = webob.Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


def index(request):
    return webob.Response(body='use lar', content_type='text/plain')

router = {
    'hello': hello,
    '/': index
}


@wsgify
def application_v4(request):
    return router.get(request.path)(request)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 9001, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
