import json
import time
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.log import app_log


class ArgumentHandler(RequestHandler):
    def get(self):
        self.write('hello {0}'.format(self.get_argument('name')))


class ArgumentsHandler(RequestHandler):
    def get(self):
        self.write('hello {0}'.format(', '.join(self.get_arguments('name'))))


class BodyHandler(RequestHandler):
    def post(self):
        body = json.loads(self.request.body.decode())
        app_log.warning(self.request.body.decode())
        self.write('hello {0}'.format(body['name']))


class PathArgsHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write('hello {0}'.format(args[0]))


class PathKwargsHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write('hello {0}'.format(kwargs['name']))


class RemoteIpHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write(self.request.remote_ip)


class FobiddenHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.set_status(403)
        self.write('forbiden')


class CustomStatusHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.set_status(498, reason='custom error')
        self.finish()


class HeaderHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.add_header('X-Header', 'xxxxx')
        self.add_header('x-Header', 'yyyyy')
        self.write('hello')


class MultiWriteHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write('start\n')
        self.flush()
        for x in range(10):
            self.write('{0}\n'.format(x))
            self.flush()
            time.sleep(0.1)
        self.finish('complete')


if __name__ == '__main__':
    app = Application(
            [
                (r'/', ArgumentHandler),
                (r'/args', ArgumentsHandler),
                (r'/body', BodyHandler),
                (r'/path/args/(.*)', PathArgsHandler),
                (r'/path/kwargs/(?P<name>.*)', PathKwargsHandler),
                (r'/ip', RemoteIpHandler),
                (r'/403', FobiddenHandler),
                (r'/498', CustomStatusHandler),
                (r'/head', HeaderHandler),
                (r'/multi', MultiWriteHandler)
            ]
    )
    app.listen(port=8001, address='0.0.0.0')
    IOLoop.current().start()
