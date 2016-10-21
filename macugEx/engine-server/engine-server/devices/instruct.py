# -*- coding: utf-8 -*-
"""
指令处理模块,以 _0x 开头的函数为具体指令处理函数
入参数: (DeviceConnect, 指令参数)
       具体指令参数见通信文档
返回值: (模式, 参数)
模式有: send 发送参数数据
       recv 收到腕表指令
       last 与腕表交互最后一条指令
       stop 断开腕表长连接
"""
import logging
from time import time

logger = logging.getLogger('watch.instruct')


def type_01(conn, data):
    """
    登录指令
    """
    logger.warning('%s relogin happed' % conn.imei)
    dev = conn.model
    dev.reload(retain=True)
    dev.heartbeat = data.get('heartbeat', 300)
    dev.save()
    return 'send', {'status': 200}


def type_002(conn, data):
    """
    对时指令
    """
    return 'send', {'time': time()}


def type_3(conn, data):
    """
    心跳指令
    """
    return 'send', {}
