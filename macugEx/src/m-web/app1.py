from urllib.parse import parse_qs
from html import escape
import os


class Request:
    def __init__(self, environ):
        self.params = parse_qs(environ.get('QUERY_STRING'))
        self.path = environ.get('PATH_INFO')
        self.method = environ.get('REQUEST_METHOD')
        self.body = environ.get('wsgi.input')
        self.headers = {}
        server_env = os.environ
        for k, v in environ.items():
            if k not in server_env.keys():
                self.headers[k.lower()] = v


class Response:
    STATUS = {
        200: 'OK',
        404: 'Not Found'
    }

    def __init__(self, body=None):
        if body is None:
            body = ''
        self.body = body
        self.status = '200 OK'
        self.headers = {
            'content-type': 'text/html',
            'content-length': str(len(self.body))
        }

    def set_body(self, body):
        self.body = body
        self.headers['content-length'] = str(len(self.body))

    def set_status(self, status_code, status_text=''):
        self.status = '{} {}'.format(status_code, self.STATUS.get(status_code, status_text))

    def set_header(self, name, value):
        self.headers[name] = value

    def __call__(self, start_response):
        start_response(self.status, [(k, v) for k, v in self.headers.items()])
        return [self.body.encode()]


def application(environ, start_response):
    request = Request(environ)
    name = request.params.get('name', ['anon'])[0]
    body = 'hello {}'.format(escape(name))
    resp = Response(body)
    return resp(start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
