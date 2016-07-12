from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import options, define

define('port', default=8000, type=int, help='server port')
define('test', default='test', type=str, help='test')


class MainHandler(RequestHandler):
    def get(self):
        self.write('hello world,  {0}'.format(self.application.options.test))


if __name__ == '__main__':
    import os
    if os.path.exists('/etc/helloworld.conf'):
        options.parse_config_file('/etc/helloworld.conf')
    if os.path.exists('./application.conf'):
        options.parse_config_file('./application.conf')
    options.parse_command_line()
    app = Application(
        [
            (r'/', MainHandler)
        ], debug=True
    )
    setattr(app, 'options', options)
    app.listen(port=options.port, address='0.0.0.0')
    IOLoop.current().start()
