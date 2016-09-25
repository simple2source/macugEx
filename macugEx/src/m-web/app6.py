import re
from html import escape
from collections import namedtuple
from webob import Response
from webob.dec import wsgify


PATTERNS = {
    'str': '[^/].+',
    'word': '\w+',
    'any': '.+',
    'int': '[+-]?\d+',
    'float': '[+-]?\d+\.\d+'
}

CASTS = {
    'str': str,
    'word': str,
    'any': str,
    'int': int,
    'float': float
}


Route = namedtuple('Route', ['pattern', 'methods', 'casts', 'handler'])


class Router:
    def __init__(self, prefix='', domain=None):
        self.routes = []
        self.domain = domain
        self.prefix = prefix

    def _route(self, rule, methods, handler):
        pattern, casts = self._rule_parse(rule)
        self.routes.append(Route(re.compile(pattern), methods, casts, handler))

    def _rule_parse(self, rule):
        pattern = []
        spec = []
        casts = {}
        is_spec = False
        for c in rule:
            if c == '{' and not is_spec:
                is_spec = True
            elif c == '}' and is_spec:
                is_spec = False
                name, p, c = self._spec_parse(''.join(spec))
                spec = []
                pattern.append(p)
                casts[name] = c
            elif is_spec:
                spec.append(c)
            else:
                pattern.append(c)
        return '{}$'.format(''.join(pattern)), casts

    def _spec_parse(self, src):
        tmp = src.split(':')
        if len(tmp) > 2:
            raise Exception('error pattern')
        name = tmp[0]
        type = 'str'
        if len(tmp) == 2:
            type = tmp[1]
        pattern = '(?P<{}>{})'.format(name, PATTERNS[type])
        return name, pattern, CASTS[type]

    def route(self, pattern, methods=None):
        if methods is None:
            methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTION')

        def dec(fn):
            self._route(pattern, methods, fn)
            return fn
        return dec

    def _domain_match(self, request):
        return self.domain is None or re.match(self.domain, request.host)

    def _prefix_match(self, request):
        return request.path.startswith(self.prefix)

    def match(self, request):
        if self._domain_match(request) and self._prefix_match(request):
            for route in self.routes:
                if request.method in route.methods:
                    m = route.pattern.match(request.path.replace(self.prefix, '', 1))
                    if m:
                        request.args = {}
                        for k, v in m.groupdict().items():
                            request.args[k] = route.casts[k](v)
                        return route.handler


class Application:
    def __init__(self, **options):
        self.routers = []
        self.options = options

    def add_router(self, router):
        self.routers.append(router)

    @wsgify
    def __call__(self, request):
        for router in self.routers:
            handler = router.match(request)
            if handler:
                return handler(self, request)


r1 = Router(domain='python.magedu.com')
r2 = Router('/r2')


@r1.route('/')
def main(app, request):
    return Response("this is man page")


@r2.route('/hello/{name}/{age:int}')
def hello(app, request):
    print(request.args['age'])
    print(type(request.args['age']))
    body = 'hello {}'.format(escape(request.args.get('name')))
    return Response(body)


@r1.route('/favicon.ico')
def favicon(app, request):
    with open('./favicon.ico', 'rb') as f:
        resp = Response(body=f.read(), content_type='image/x-icon')
        return resp


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = Application()
    app.add_router(r1)
    app.add_router(r2)
    server = make_server('0.0.0.0', 3000, app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
