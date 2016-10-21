# -*- coding: utf-8 -*-
#
# engine project configure file
#
import logging
version = '0.1'

devices = {
    'worker': 1,
    'host': '0.0.0.0',
    'port': 8000,
    'uri': '127.0.0.1',
    'debug': True,
    'sock_timeout': 360,
    'loglevel': logging.DEBUG,
    'logfile': './devices/server.log',
};

app = {
    'host': '0.0.0.0',
    'port': 8080,
    'uri': '127.0.0.1',
    'debug': True,
    'loglevel': logging.DEBUG,
    'logfile': './app/error.log',
};

admin = {
    'host': '0.0.0.0',
    'port': 46123,
    'uri': '127.0.0.1',
    'salt': 'UVWBQ5KiiFhShHzoiyQ6hKtnKQVyFKhfId4PnkF6LQA=',
    'debug': True,
    'loglevel': logging.DEBUG,
    'logfile': './admin/error.log',
};

agent = {
    'host': '127.0.0.1',
    'request_port': 8003,
    'respond_port': 8004,
    'port': 8005,
    'loglevel': logging.DEBUG,
    'logfile': './agent/broker.log'
};

static = {
    'use_nginx': False,  # 是否使用nginx处理文件传输
    'use_local': False,  # 是否使用unix域socket
    'use_port': 80,  # 若使用tcp socket时绑定的端口
    'debug': True,
    'uri': '127.0.0.1',  # 未用到
    'normal_size': (240, 240),  # 圈子,腕表,用户 app端接收头像缩略图
    'small_size': (70, 70),  # 圈子,腕表,用户 腕表端接收头像缩略图
    'loglevel': logging.INFO,
    'logfile': './static/error.log',
    'storage': 'file'
};

mqtt = {
    'host': '127.0.0.1',
    'port': 1883,
    'username': 'admin',
    'password': 'admin',
    'cli_username': 'YK01',
    'cli_password': 'YK01',
    'prefix': 'YK01',
};

push = {
    'host': '127.0.0.1',
    'port': 8002,
    'loglevel': logging.INFO,
    'logfile': './push/push.log',
    'identify': {
        "com.YK.iot": {
            "develop": "./push/cert/develop.pem",
            "produce": "./push/cert/produce.pem",
            "password": "1234"
        }
    }
};

mongo = {
    'host': '127.0.0.1',
    'port': 27017,
    'database': 'YK01',
    'username': None,
    'password': None,
};

redis = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': None,
};
