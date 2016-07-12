import os
from tornado.options import options
from tornado.ioloop import IOLoop
from logscan import make_app
from logscan.hendlers import WatcherHandler
from logscan.hendlers import RuleHandler

router = [
    (r'/watcher', WatcherHandler),
    (r'/rule', RuleHandler)
]


if __name__ == '__main__':
    if os.path.exists('/etc/logscan-api.conf'):
        options.parse_config_file('/etc/logscan-api.conf')
    if os.path.exists('./application.conf'):
        options.parse_config_file('./application.conf')
    options.parse_command_line()
    app = make_app(router, debug=True)
    app.listen(options.port, address=options.bind)
    try:
        app.zk.start()
        IOLoop.current().start()
    except KeyboardInterrupt:
        app.zk.stop()
        IOLoop.current().stop()