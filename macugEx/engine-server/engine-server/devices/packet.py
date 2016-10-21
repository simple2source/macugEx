# -*- coding: utf-8 -*-
"""
指令解析处理模块
从socket读取指令
解析指令参数
将指令参数打包成数据
"""
from struct import pack, unpack
from gevent import socket
from random import randint
import json

__all__ = ['extract', 'assemble']


def extract(sock, extra):
    """
    cacheable recv data from socket
    :param extra: last time remain data
                  splice it into now
    ___________________________________________
    |  length  |        data          | extra
    -------------------------------------------
    从socket中提取一个指令数据
    并返回剩余数据下次解析使用
    """
    if len(extra) < 4:
        packet = sock.recv(1024)
        if not packet and not extra:
            raise socket.error
        if extra:
            packet = extra + packet
    else:
        packet = extra
    while len(packet) < 4:
        complement = sock.recv(1024)
        if not complement:
            raise socket.error
        packet += complement
    length = unpack('>I', packet[:4])[0]
    if length:
        packet = packet[4:]
        while len(packet) < length:
            complement = sock.recv(1024)
            if not complement:
                raise socket.error
            packet += complement
        extra_data = packet[length:]
        data = json.loads(packet[:length])
    else:
        data = {}
        extra_data = packet[4:]
    return data, extra_data


def assemble(data):
    """
    __________________________________
    |  length  |         data
    ----------------------------------
    将数据组装成完整数据包
    :param ident: <str>
    :param itype: <str>
    :param data: <str>
    """
    if not data.get('ident'):
        data['ident'] = randint(0, 65535)
    data = json.dumps(data)
    pkd_length = len(data)
    pkg_length = pack('>I', pkd_length)
    return pkg_length + data
