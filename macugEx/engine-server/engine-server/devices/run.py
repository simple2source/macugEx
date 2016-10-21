# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_os()
monkey.patch_socket()
monkey.patch_thread(Event=True)
monkey.patch_time()
from gevent.server import StreamServer
from gevent import socket
from multiprocessing import Process
import gevent
import sys
import os
import logging
from logging.handlers import RotatingFileHandler

sys.path.append('..')
import conf

from device import DeviceConnect, device_upon, device_offs, generate_dispose
from packet import extract

server_timeout = conf.devices['sock_timeout']


def handle(sock, address):
    imei = 0
    try:
        sock.settimeout(server_timeout)
        # 初始化连接
        data, extra_data = extract(sock, '')
        imei = data['imei']
        ident = data['ident']
        dc = DeviceConnect(sock, imei)
        dc._extra_data = extra_data
        # 与腕表建立连接完成,设置连接超时时间
        heartbeat = data['heartbeat']
        sock.settimeout(heartbeat + 30)
        # 登陆处理
        dc.login(ident, address[0], data)
        gevent.spawn(dc.login_handle)
        # 腕表上线
        device_upon(address, imei, dc)
        dc.loop()
    except socket.error:
        pass
    except:
        logger.error('%s %s' % (imei, repr(address)), exc_info=True)
    finally:
        if imei:
            device_offs(address, imei)


logger = logging.getLogger('watch')

logfile = os.path.abspath(os.path.join(os.path.dirname(conf.__file__), conf.devices['logfile']))
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(conf.devices['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(conf.devices['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if not issubclass(exc_type, (KeyboardInterrupt, SystemExit, SystemError)):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if conf.devices['debug']:
    printlog = logging.StreamHandler()
    printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
    printlog.setLevel(conf.devices['loglevel'])
    logger.addHandler(printlog)

if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    host = '0.0.0.0' if conf.devices['host'] != '127.0.0.1' else conf.devices['host']
    server = StreamServer((host, conf.devices['port']), handle, backlog=1024)
    server.init_socket()
    server.max_accept = 1


    def serve_forever():
        dispose = generate_dispose()
        dispose.start()
        try:
            server.start()
            print('Serving Start on %s port %s ...' % (host, conf.devices['port']))
            try:
                server._stop_event.wait()
            except:
                raise
        except KeyboardInterrupt:
            pass


    for i in range(conf.devices['worker'] - 1):
        Process(target=serve_forever, args=tuple()).start()
    serve_forever()
