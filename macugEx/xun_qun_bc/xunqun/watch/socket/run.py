# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_all(Event=True, dns=False)
from gevent.server import StreamServer
from gevent import socket
from multiprocessing import Process
import gevent
import sys
import logging
from logging.handlers import RotatingFileHandler

sys.path.append('../..')
import setting

from device import DeviceConnect, device_upon, device_offs, generate_dispose
from instruct import build_question_to_medal
from packet import extract

server_timeout = setting.server['sock_timeout']


def handle(sock, address):
    imei = 0
    try:
        sock.settimeout(server_timeout)
        # 初始化连接
        version, identify, itype, params, extra_data = extract(sock, '')
        if itype != '\x01':
            logger.warning('illegal login instruct:0x%x %s' % (ord(itype), repr(address)))
            return None
        imei = params[0]
        dc = DeviceConnect(sock, imei)
        dc._extra_data = extra_data
        # 与腕表建立连接完成,设置连接超时时间
        heartbeat = params[3]
        sock.settimeout(heartbeat + 30)
        # 登陆处理
        dc.login(identify, address[0], params)
        gevent.spawn(dc.login_handle)
        # 腕表上线
        device_upon(address, imei, dc)
        dc.loop()
    except socket.error:
        pass
    except:
        if imei:
            logger.error('%s %s' % (imei, repr(address)), exc_info=True)
    finally:
        if imei:
            device_offs(address, imei)


logger = logging.getLogger('watch')

logfile = setting.server['logfile']
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(setting.server['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(setting.server['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if setting.server['debug']:
    printlog = logging.StreamHandler()
    printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
    printlog.setLevel(setting.server['loglevel'])
    logger.addHandler(printlog)

if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    server = StreamServer(('0.0.0.0', setting.server['sock_port']), handle, backlog=1024)
    server.init_socket()
    server.max_accept = 1


    def serve_forever():
        build_question_to_medal()

        dispose = generate_dispose()
        dispose.start()
        try:
            server.start()
            try:
                server._stop_event.wait()
            except:
                raise
        except KeyboardInterrupt:
            pass


    for i in range(setting.server['worker'] - 1):
        Process(target=serve_forever, args=tuple()).start()
    serve_forever()
