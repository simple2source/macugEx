from html import escape
from webob import Request, Response


def application(environ, start_response):
    request = Request(environ)
    name = request.params.get('name', 'anon')
    body = 'hello {}'.format(escape(name))
    resp = Response(body)
    return resp(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
