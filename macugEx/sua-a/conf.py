# -*- coding: utf-8 -*-
from os import path
import logging

# ----------------------
# app server config
# ----------------------

app = {
    'host': '0.0.0.0',  # 应用监听地址
    'port': 8080,  # 应用监听端口
    'debug': True,  # 应用调试级别
    'file': 'error.log',  # 日志文件路径(相对于执行文件所在目录)
    'base_url': 'http://127.0.0.1:8080',  # 访问本地服务的 index 链接
    'static_path': path.join(path.dirname(path.abspath(__file__)), './static'),  # 存储静态文件的本地路径
    'CorpID': 'xxxxxx',  # 微信企业号CorpID
    'Secret': 'xxxxxx',  # 微信企业号Secret
}

STATIC_URL = '%s/static' % app['base_url']  # 静态文件url
STATIC_PATH = app['static_path']  # 静态文件目录

# ----------------------
# mongodb driver config
# ----------------------

mongodb = {
    'host': '127.0.0.1',
    'port': 27017,
    'username': None,
    'password': None,
    'database': 'suaa'
}

# ----------------------
# admin manage config
# ----------------------

admin = {
    'host': '127.0.0.1',
    'debug': True,
    'salt': 'UVWBQ5KiiFhShHzoiyQ6hKtnKQVyFKhfId4PnkF6LQA=',
    'loglevel': logging.DEBUG,
    'logfile': './error.log',
}