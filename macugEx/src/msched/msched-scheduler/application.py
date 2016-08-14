import os
from tornado.options import options, define, parse_command_line, parse_config_file
from scheduler import Scheduler

define('hosts', default='127.0.0.1:2181', type=str, help='zookeeper hosts')
define('root', default='/msched', type=str, help='zookeeper root node')

if __name__ == '__main__':
    if os.path.exists('/etc/msched/scheduler.conf'):
        parse_config_file('/etc/msched/scheduler.conf')
    if os.path.exists('./application.conf'):
        parse_config_file('./application.conf')
    parse_command_line()
    scheduler = Scheduler(hosts=options.hosts, root=options.root)
    scheduler.start()
    try:
        scheduler.join()
    except KeyboardInterrupt:
        scheduler.shutdown()