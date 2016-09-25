import re
from html import escape
from collections import namedtuple
from webob import Response
from webob.dec import wsgify


Route = namedtuple('Route', ['pattern', 'methods', 'handler'])


class Application:
    def __init__(self, **options):
        self.routes = []
        self.options = options

    def _route(self, pattern, methods, handler):

        self.routes.append(Route(re.compile(pattern), methods, handler))

    def route(self, pattern, methods=None):
        if methods is None:
            methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTION')

        def dec(fn):
            self._route(pattern, methods, fn)
            return fn
        return dec

    @wsgify
    def __call__(self, request):
        for route in self.routes:
            if request.method in route.methods:
                if route.pattern.match(request.path):
                    return route.handler(self, request)


app = Application(debug=True)


@app.route(r'/$')
def main(app, request):
    return Response("this is man page")


@app.route(r'/hello$')
def hello(app, request):
    if app.options.get('debug'):
        for k, v in request.headers.items():
            print('{} => {}'.format(k, v))
    name = request.params.get('name', 'anon')
    body = 'hello {}'.format(escape(name))
    return Response(body)


@app.route(r'/favicon.ico$')
def favicon(app, request):
    with open('./favicon.ico', 'rb') as f:
        resp = Response(body=f.read(), content_type='image/x-icon')
        return resp


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 3000, app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
