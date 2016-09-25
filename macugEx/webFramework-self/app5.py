import re
from html import escape
from collections import namedtuple
from webob import Response
from webob.dec import wsgify


Route = namedtuple('Route', ['pattern', 'methods', 'handler'])


class Router:
    def __init__(self, prefix='', domain=None):
        self.routes = []
        self.domain = domain
        self.prefix = prefix

    def _route(self, pattern, methods, handler):
        self.routes.append(Route(re.compile(pattern), methods, handler))

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
                        request.args = m.groupdict()
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


@r1.route(r'/$')
def main(app, request):
    return Response("this is man page")


@r2.route(r'/hello/(?P<name>\w+)$')
def hello(app, request):
    body = 'hello {}'.format(escape(request.args.get('name')))
    return Response(body)


@r1.route(r'/favicon.ico$')
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
