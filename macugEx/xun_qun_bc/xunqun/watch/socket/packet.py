# -*- coding: utf-8 -*-
"""
指令解析处理模块
从socket读取指令
解析指令参数
将指令参数打包成数据
"""
from struct import pack as _pack, unpack
from gevent import socket
from binascii import b2a_hex

__all__ = ['extract', 'assemble']


def login_unpack(data):
    bcd_imei, bcd_imsi, bcd_mac, heartbeat = unpack('>8s8s8sI', data[:28])
    if len(data) == 40:
        soft_ver, blue_ver, bcd_customer_id, _ = unpack('>II2sH', data[28:])
        return b2a_hex(bcd_imei)[1:], b2a_hex(bcd_imsi)[1:], b2a_hex(bcd_mac)[4:], heartbeat, \
               soft_ver, blue_ver, int(b2a_hex(bcd_customer_id))
    return b2a_hex(bcd_imei)[1:], b2a_hex(bcd_imsi)[1:], b2a_hex(bcd_mac)[4:], heartbeat, 0, 0, 0


def locate_unpack(data):
    ltype, lon, lat, gps_timestamp, mcount = unpack('>H24s24sIH', data[0:56])
    remand = data[56:]
    lbs = [unpack('>HHHHi', remand[i * 12:(i + 1) * 12]) for i in range(mcount)]
    lon = lon.rstrip('\x00')
    lat = lat.rstrip('\x00')
    lon = float(lon.decode('utf-16-be')) if lon else 0
    lat = float(lat.decode('utf-16-be')) if lat else 0
    lbs_timestamp = unpack('>I', remand[-4:])[0]
    return ltype, lon, lat, gps_timestamp, lbs, lbs_timestamp


def sms_unpack(data):
    phone_length = unpack('>H', data[:2])[0]
    phone = data[2:2 + phone_length].decode('utf-16-be')
    c_start = 6 + phone_length
    content_length = unpack('>I', data[2 + phone_length:c_start])[0]
    content = data[c_start:c_start + content_length].decode('utf-16-be')
    return phone, content


def story_id_unpack(data):
    return b2a_hex(data)


def gps_status_unpack(data):
    return unpack('>BBBB', data)[:3]


def answer_game_unpack(data):
    start_timestamp, end_timestamp, _, num = unpack('>IIHH', data[:12])
    data = data[12:]
    answer = []
    for _ in range(num):
        qid, opt, result = unpack('>12sHH', data[:16])
        answer.append([b2a_hex(qid), opt, result])
        data = data[16:]
    return start_timestamp, end_timestamp, answer


unpack_handler = {
    '\x01': login_unpack,
    '\x05': locate_unpack,
    '\x07': lambda data: unpack('>I', data)[0],
    '\x0b': lambda data: unpack('>I', data)[0],
    '\x17': lambda data: unpack('>I', data)[0],
    '\x1d': lambda data: unpack('>I', data)[0],
    '\x1f': sms_unpack,
    '\x29': story_id_unpack,
    '\x35': lambda data: ord(data),
    '\x3d': lambda data: unpack('>I', data)[0],
    '\x3f': gps_status_unpack,
    '\x43': lambda data: b2a_hex(unpack('>8s', data)[0])[4:],
    '\x45': answer_game_unpack,
    '\x4b': story_id_unpack,
}


def extract(sock, extra):
    """
    cacheable recv data from socket
    :param extra: last time remain data
                  splice it into now
    ___________________________________________
    |\x00|ident|instruct|length| data | extra |
    -------------------------------------------
    从socket中提取一个指令报文
    并返回剩余数据下次解析使用
    """
    if len(extra) < 8:
        data = sock.recv(1024)
        if not data and not extra:
            raise socket.error
        if extra:
            data = extra + data
    else:
        data = extra
    while len(data) < 8:
        complement = sock.recv(1024)
        if not complement:
            raise socket.error
        data += complement
    version, identify, itype, length = unpack('>B2s1sI', data[:8])
    if length:
        data = data[8:]
        while len(data) < length:
            complement = sock.recv(1024)
            if not complement:
                raise socket.error
            data += complement
        params = unpack_handler[itype](data[:length])
        extra_data = data[length:]
    else:
        params = ()
        extra_data = data[8:]
    return version, identify, itype, params, extra_data


def assemble(ident, itype, data):
    """
    __________________________________
    |\x00|ident|instruct|length| data |
    ----------------------------------
    将数据组装成完整数据包
    :param ident: <str>
    :param itype: <str>
    :param data: <str>
    """
    pkd_length = len(data)
    pkg_length = _pack('>I', pkd_length)
    return '\x00' + ident + itype + pkg_length + data
