# -*- coding:utf-8 -*-

import re
import webob
from webob.dec import wsgify
from webob import exc

# ---------v6 blueprint------=>


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



class Router(object):
    def __init__(self, prefix=''):
        self.__prefix = prefix.rstrip('/')
        self._routes = []

    @property
    def prefix(self):
        return self.__prefix

    def route(self, pattern='.*', methods=None):
        def wrap(handler):
            self._routes.append((re.compile(pattern), handler, methods))
            return handler
        return wrap

    def get(self, pattern='.*'):
        return self.route(pattern, 'GET')

    def post(self, pattern='.*'):
        return self.route(pattern, 'POST')

    def delete(self, pattern='.*'):
        return self.route(pattern, 'DELETE')

    def run(self, request):
        if request.path.startswith(self.prefix):
            return None
        for pattern, handler, methods in self._routes:
            if methods:
                if isinstance(methods, (list, tuple, set)) and request.method not in methods:
                    continue
                if isinstance(methods, str) and request.method != methods.upper():
                    continue
                m = pattern.match(request.path.replace(self.prefix, '', 1))
                if m:
                    request.args = m.groups()
                    request.kwargs = _Vars(m.groupdict())
                    return handler(request)


class Application(object):
    ROUTERS = []

    @classmethod
    def register(cls, router):
        cls.ROUTERS.append(router)

    @wsgify
    def __call__(self, request):
        for route in self.ROUTERS:
            response = route.run(request)
            if response:
                return response
        raise exc.HTTPNotFound('not found')


knife = Router('/knife')
Application.register(knife)


@knife.get(r'/(?P<id>\d+)$')
def buy(request):
    return webob.Response(body='buy {}'.format(request.kwargs.get(id)))

# ---------v7 cancel re------=>

PATTERNS = {
    'str': r'[^/]+',
    'word': r'\w+',
    'int': r'[+-]?\d+',
    'float': r'[+-]?\d+.\d+',
    'any': r'.+'

}

TRANSLATORS = {
    'str': str,
    'word': str,
    'any': str,
    'int': int,
    'float': float
}


class Route(object):
    __slots__ = ['methods', 'pattern', 'translator', 'handler']

    def __init__(self, pattern, translator, methods, handler):
        self.pattern = re.compile(pattern)
        if translator is None:
            self.translator = {}
        self.translator = translator
        self.methods = methods
        self.handler = handler

    def run(self, prefix, request):
        if self.methods:
            if isinstance(self.methods, (list, tuple, set)) and request.method not in self.methods:
                return
            if isinstance(self.methods, str) and request.method != self.methods.upper():
                return
            m = self.pattern.match(request.path.replace(prefix, '', 1))
            if m:
                vs = {}
                for k, v in m.groupdict().items():
                    vs[k] = self.translator[k](v)
                request.vars = _Vars(vs)
                return self.handler(request)


class Router(object):
    def __init__(self, prefix=''):
        self.__prefix = prefix
        self._routes = []

    def _rule_parse(self, rule):
        pattern = ['^']
        spec = []
        translator = {}
        is_spec = False
        # /home/{name:str}/{id:int}
        for c in rule:
            if c == '{':
                is_spec = True
            elif c == '}':
                is_spec = False
                name, pat, t = self._spec_parse(''.join(spec))
                pattern.append(pat)
                translator[name] = t
                spec = []
            elif is_spec:
                spec.append(c)
            else:
                pattern.append(c)

    @staticmethod
    def _spec_parse(spec):
        name, _, type = spec.partiton(':')
        if not name.isidentifier():
            raise Exception('name {} is not identifier'.format(name))
        if type not in PATTERNS.keys():
            type = 'word'
        pattern = '(?P<{}>{})'.format(name, PATTERNS[type])
        return name, pattern, TRANSLATORS[type]

    def route(self):
        pass






if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9003, Application())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
