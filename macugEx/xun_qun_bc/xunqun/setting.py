# -*- coding: utf-8 -*-
__all__ = ['server', 'app', 'admin', 'push', 'broker', 'email', 'mqtt', 'mongo', 'redis']

import logging

server = {
    'worker': 1,
    'sock_port': 8000,
    'http_port': 8001,
    'conf_port': 9892,
    'sock_uri': 's.ios16.com',  # 未用到
    'http_uri': 'h.ios16.com',  # 未用到
    'debug': True,
    'sock_timeout': 360,
    'almanac_timeout': 3600 * 24,  # 星历文件过期时间
    'loglevel': logging.DEBUG,
    'logfile': './server.log',
}

app = {
    'debug': True,
    'port': 8080,
    'uri': 'app.ios16.com',  # 未用到
    'loglevel': logging.DEBUG,
    'logfile': './error.log',
}

static = {
    'use_nginx': False,  # 是否使用nginx处理文件传输
    'use_local': False,  # 是否使用unix域socket
    'use_port': 80,  # 若使用tcp socket时绑定的端口
    'debug': True,
    'uri': 'static.ios16.com',
    'normal_size': (240, 240),  # 圈子,腕表,用户 app端接收头像缩略图
    'small_size': (70, 70),  # 圈子,腕表,用户 腕表端接收头像缩略图
    'loglevel': logging.DEBUG,
    'logfile': './error.log',
    'storage': 'file',  # 静态文件存储: 'file' or 'mongodb'
}

admin = {
    'host': '127.0.0.1',
    'port': 46123,
    'debug': True,
    'uri': 'web.ios16.com',  # 未用到
    'salt': 'UVWBQ5KiiFhShHzoiyQ6hKtnKQVyFKhfId4PnkF6LQA=',
    'loglevel': logging.DEBUG,
    'logfile': './error.log',
}

push = {
    'host': '127.0.0.1',
    'port': 8002,
    'loglevel': logging.DEBUG,
    'logfile': './push.log',
}

broker = {
    'host': '127.0.0.1',
    'request_port': 8003,
    'respond_port': 8004,
    'channel_port': 8005,
    'loglevel': logging.DEBUG,
    'logfile': './broker.log'
}

mqtt = {
    'host': '127.0.0.1',
    'port': 1883,
    'username': 'admin',
    'password': 'admin',
    'cli_username': 'YK01',
    'cli_password': 'YK01',
    'prefix': 'YK01',
}

mongo = {
    'host': '127.0.0.1',
    'port': 27017,
    'database': 'YK01',
    'username': None,
    'password': None,
}

redis = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': None,
}

LocateProxy = {
    'host': '127.0.0.1',
    'port': 8006,
    'loglevel': logging.DEBUG,
    'logfile': './proxy.log',
}
