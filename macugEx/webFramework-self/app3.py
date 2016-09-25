import re
from html import escape
from webob import Response
from webob.dec import wsgify


@wsgify
def application(request):
    if re.match(r'/favicon.ico$', request.path):
        return favicon(request)
    if re.match(r'/hello$', request.path):
        return hello(request)
    if re.match(r'/$', request.path):
        return main(request)


def main(request):
    return Response("this is man page")


def hello(request):
    name = request.params.get('name', 'anon')
    body = 'hello {}'.format(escape(name))
    return Response(body)


def favicon(request):
    with open('./favicon.ico', 'rb') as f:
        resp = Response(body=f.read(), content_type='image/x-icon')
        return resp


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
