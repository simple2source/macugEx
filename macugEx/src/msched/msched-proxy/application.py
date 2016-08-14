import os
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, parse_config_file, options
from msched import make_app
from msched.handlers import TaskHandler, TasksHandler

routes = [
    (r'/task', TaskHandler),
    (r'/task/(.*)', TaskHandler),
    (r'/tasks', TasksHandler)
]

app = make_app(routes)

if __name__ == '__main__':
    if os.path.exists('/etc/msched/proxy.conf'):
        parse_config_file('/etc/msched/proxy.conf')
    if os.path.exists('./application.conf'):
        parse_config_file('./application.conf')
    parse_command_line()
    app = make_app(routes, debug=True)
    app.listen(options.port, address=options.bind)
    try:
        app.zk.start()
        IOLoop().current().start()
    except KeyboardInterrupt:
        IOLoop().current().stop()
