# -*- coding:utf-8 -*-

import re
import webob
from webob.dec import wsgify
from webob import exc


def hello(request):
    name = request.params.get('name', 'wlp')
    response = webob.Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


def index(request):
    return webob.Response(body='use lar', content_type='text/plain')


class Application(object):
    ROUTER = {}

    @classmethod
    def register(cls, path, handler):
        cls.ROUTER[path] = handler

    def default_handler(self, request):

        # return webob.Response(body='not found', status=404)
        # use webob exepction
        return exc.HTTPNotFound('not found')

    @wsgify
    def __call__(self, request):
        # return self.ROUTER.get(request.path, self.default_handler)(request)
        try:
            self.ROUTER[request.path](request)
        except KeyError:
            raise exc.HTTPNotFound('not found')


# ---------v2 use decator handler -------->


class ApplicationV2(object):
    ROUTER = {}

    @classmethod
    def register(cls, path):
        def wrap(handler):
            cls.ROUTER[path] = handler
            return handler
        return wrap

    @wsgify
    def __call__(self, request):
        try:
            return self.ROUTER[request.path](request)
        except KeyError:
            raise exc.HTTPNotFound('not found')


@ApplicationV2.register('/')
def index(request):
    return webob.Response(body='use lar', content_type='text/plain')


@ApplicationV2.register('/hello')
def hello(request):
    name = request.params.get('name', 'webob')
    response = webob.Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


# ----------v3 pattern router------------->


class ApplicationV3(object):
    ROUTER = []

    @classmethod
    def register(cls, pattern):
        def wrap(handler):
            cls.ROUTER.append((re.compile(pattern), handler))
            return handler
        return wrap

    @wsgify
    def __call__(self, request):
        for pattern, handler in self.ROUTER:
            if pattern.match(pattern, request.path):
                return handler(request)
        raise exc.HTTPNotFound('not found')


@ApplicationV3.register('^/$')
def index(request):
    return webob.Response(body='use lar', content_type='text/plain')


@ApplicationV3.register('^/hello$')
def hello(request):
    name = request.params.get('name', 'webob')
    response = webob.Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


#  ----------v4 request.args,request.kwargs--------->


class _Vars(object):
    def __init__(self, data=None):
        if data is not None:
            self._data = data
        else:
            self._data = {}

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError('no attribute'.format(item))

    def __setattr__(self, key, value):
        if key != '_data':
            raise NotImplemented
        self.__dict__['_data'] = value


class ApplicationV4(object):
    ROUTER = []

    @classmethod
    def register(cls, pattern, method):
        def wrap(handler):
            cls.ROUTER.append((method, re.compile(pattern), handler))
            return handler
        return wrap

    def __call__(self, request):
        for method, pattern, handler in self.ROUTER:
            if method.upper() != request.method:
                continue
            m = pattern.match(request.path)
            if m:
                request.args = m.groups()
                request.kwargs = _Vars(m.groupdict())
                request.args = request.PATH_INFO
                return handler(request)
        raise exc.HTTPNotFound('not found')


@ApplicationV4.register('^/hello/(\w+)', 'get')
def index(request):
    return webob.Response(body='use lar', content_type='text/plain')


@ApplicationV4.register('^/hello/(?P<name>\w+)$', 'get')
def hello(request):
    name = request.params.get('name', 'webob')
    response = webob.Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


#  ----------v5 get\post\put in route,can use route and get to register--------->


class ApplicationV5(object):

    ROUTER = []

    @classmethod
    def route(cls, pattern=None, methods=None):
        def wraps(handler):
            cls.ROUTER.append((re.compile(pattern), handler, methods))
            return handler
        return wraps

    @classmethod
    def get(cls, pattern):
        return cls.route(pattern, 'get')

    @classmethod
    def put(cls, pattern):
        return cls.route(pattern, 'put')

    @classmethod
    def post(cls, pattern):
        return cls.route(pattern, 'post')

    def __call__(self, request):
        for pattern, handler, methods in self.ROUTER:
            if methods:
                if isinstance(methods, (tuple, list, set)) and request.method not in methods:
                    continue
                if isinstance(methods, str) and request.method != methods.upper():
                    continue
            m = pattern.match(request.path)
            if m:
                request.args = m.groups()
                request.kwargs = _Vars(m.groupdict())
                request.args = request.PATH_INFO
                return handler(request)
        raise exc.HTTPNotFound('NOT FOUND')


@ApplicationV5.get('/hello')
def hello(request):
    name = request.agrs.get('name')
    response = webob.Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


@ApplicationV5.route('/test', methods=['get', 'post'])
def test(request):
    return webob.Response(body='use lar', content_type='text/plain')

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    Application.register('/hello', hello)
    Application.register('/', index)

    server = make_server('0.0.0.0', 9002, Application())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()