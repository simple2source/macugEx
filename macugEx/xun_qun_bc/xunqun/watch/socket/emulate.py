# -*- coding: utf-8 -*-
"""
模拟器类
"""
import threading
import socket

try:
    import Queue
except ImportError:
    import queue as Queue
import datetime
import struct
import random
import time
import click
import binascii


def pack_locate(*args):
    ltype = args[0]
    lon = args[1]
    lat = args[2]
    mcount = args[3]
    cells = args[4]
    timestamp = args[5]

    lon = str(lon).encode('utf-16-be')
    lat = str(lat).encode('utf-16-be')
    slon = lon + '\x00' * (24 - len(lon))
    slat = lat + '\x00' * (24 - len(lat))
    prefix = struct.pack('>H24s24sIH', ltype, slon, slat, timestamp, mcount)
    lbs = ''.join([struct.pack('>HHHHi', c[0], c[1], c[2], c[3], c[4]) for c in cells])

    data = prefix + lbs + struct.pack('>I', timestamp)
    return data


def pack_sms(*args):
    phone, content = args
    phone = phone.encode('utf-16-be')
    phone_length = len(phone)
    if isinstance(content, str):
        content = content.decode('utf-8').encode('utf-16-be')
    elif isinstance(content, unicode):
        content = content.encode('utf-16-be')
    content_length = len(content)
    data = struct.pack('>H%ssI%ss' % (phone_length, content_length), phone_length, phone, content_length, content)
    return data


def pack_strategy(strategy):
    data = struct.pack('>B', strategy)
    return data


def pack_login(imei, imsi, mac, heartbeat, software_v, bluetooth_v, customer_id):
    return struct.pack('>QQQIIII', int(str(imei), 16), int(str(imsi), 16), int(mac, 16), heartbeat,
                       software_v, bluetooth_v, customer_id)


def pack_answer_game(time1, time2, answer_list):
    answer_list_pack = []
    for answer in answer_list:
        answer_list_pack.append(struct.pack('>12sHH', binascii.a2b_hex(answer[0]), answer[1], answer[2]))
    answer_list_data = ''.join(answer_list_pack)
    return struct.pack('>IIHH', time1, time2, 0, len(answer_list)) + answer_list_data


pack_handler = {
    '\x01': pack_login,
    '\x02': lambda: '',
    '\x03': lambda: '',
    '\x04': lambda: '',
    '\x05': pack_locate,
    '\x06': lambda: '',
    '\x07': lambda: '',
    '\x08': lambda: '',
    '\x0a': lambda: '',
    '\x0b': lambda: '',
    '\x0c': lambda: '',
    '\x0e': lambda: '',
    '\x10': lambda: '',
    '\x12': lambda: '',
    '\x14': lambda: '',
    '\x16': lambda: '',
    '\x17': lambda percent: struct.pack('>I', percent),
    '\x18': lambda: '',
    '\x1a': lambda: '',
    '\x1b': lambda: '',
    '\x1c': lambda: '',
    '\x1d': lambda errno: struct.pack('>I', errno),
    '\x1e': lambda: '',
    '\x1f': pack_sms,
    '\x20': lambda: '',
    '\x22': lambda: '',
    '\x24': lambda: '',
    '\x26': lambda: '',
    '\x28': lambda: '',
    '\x29': lambda story_id: binascii.a2b_hex(story_id),
    '\x31': lambda: '',
    '\x33': lambda: '',
    '\x34': lambda: '',
    '\x35': pack_strategy,
    '\x36': lambda: '',
    '\x37': lambda: '',
    '\x38': lambda: '',
    '\x3a': lambda: '',
    '\x3c': lambda: '',
    '\x3d': lambda heartbeat: struct.pack('>I', heartbeat),
    '\x3f': lambda a, b, c: struct.pack('>BBBB', a, b, c, 0),
    '\x40': lambda: '',
    '\x41': lambda: '',
    '\x42': lambda: '',
    '\x43': lambda mac: struct.pack('>Q', int(mac, 16)),
    '\x44': lambda: '',
    '\x45': pack_answer_game,
    '\x46': lambda: '',
    '\x48': lambda: '',
    '\x4a': lambda: '',
    '\x4b': lambda story_id: binascii.a2b_hex(story_id),
}


def pack_data(ident, itype, params):
    data = pack_handler[itype](*params)
    pkd_length = len(data)
    pkg_length = struct.pack('>I', pkd_length)
    return '\x00' + ident + itype + pkg_length + data


def unpack_login(data):
    login_status = ord(data[0])
    if login_status == 1:
        watch_status = ord(data[1])
        crypt = data[2:]
        return login_status, watch_status, crypt.decode('utf-16-be')
    else:
        ip = [str(ord(data[2])), str(ord(data[3])), str(ord(data[4])), str(ord(data[5]))]
        ip = '.'.join(ip)
        address = u'%s:%s' % (ip, struct.unpack('>H', data[6:8])[0])
        return login_status, address


def unpack_group_contact_diff(data):
    length = struct.unpack('>I', data[:4])[0]
    text = struct.unpack('>%ss' % length, data[4:4 + length])[0]
    return length, text.decode('utf-16-be')


def unpack_group_message(data):
    m_type, a_length, m_id, s_id = struct.unpack('>HH12s12s', data[:28])
    content_length = struct.unpack('>I', data[28:32])[0]
    content = struct.unpack('>%ss' % content_length, data[32:32 + content_length])[0]
    return m_type, a_length, binascii.b2a_hex(m_id), binascii.b2a_hex(s_id), content.decode('utf-16-be')


def unpack_watch_alarm(data):
    num = struct.unpack('>H', data[:2])[0]
    alarm_data = data[2:]
    alarm_list = []
    while alarm_data:
        status, cycle_num, hour, minute, l_length = struct.unpack('>BBBBH', alarm_data[:6])
        label = alarm_data[6:6 + l_length].decode('utf-16-be')
        alarm_data = alarm_data[6 + l_length:]
        alarm_list.append((status, '{0:08b}'.format(cycle_num), '%02d:%02d' % (hour, minute), l_length, label))
    return num, alarm_list


def unpack_send_story(data):
    story_id = binascii.b2a_hex(data[0:12])
    content_url_len = struct.unpack('>H', data[12:14])[0]
    content_url = data[14:].decode('utf-16-be')
    return story_id, content_url_len, content_url


def unpack_delete_story(data):
    return binascii.b2a_hex(data)


def unpack_a_key_call(data):
    phone_len = struct.unpack('>I', data[:4])[0]
    phone = data[4:].decode('utf-16-be')
    return phone_len, phone


def unpack_almanac(data):
    url_len = struct.unpack('>I', data[:4])[0]
    url = data[4:-4].decode('utf-16-be')
    timestamp = struct.unpack('>I', data[-4:])[0]
    return url_len, url, timestamp


def unpack_monitor(data):
    phone_len = struct.unpack('>I', data[:4])[0]
    phone = data[4:].decode('utf-16-be')
    return phone_len, phone


def unpack_lbs_faceback(data):
    lon, lat, timestamp = struct.unpack('>24s24sI', data)
    lon = lon.rstrip('\x00')
    lat = lat.rstrip('\x00')
    lon = float(lon.decode('utf-16-be'))
    lat = float(lat.decode('utf-16-be'))
    return lon, lat, timestamp


def unpack_bluetooth(data):
    file_length = struct.unpack('>I', data[:4])[0]
    file_url = data[4:4 + file_length].decode('utf-16-be')
    version = struct.unpack('>I', data[4 + file_length:])[0]
    return file_length, file_url, version


def unpack_answer_game(data):
    title_len = struct.unpack('>I', data[:4])[0]
    title = data[4:4 + title_len].decode('utf-16-be')
    answer_num = struct.unpack('>H', data[4 + title_len:6 + title_len])[0]
    data = data[6 + title_len:]
    question_list = []
    for i in range(answer_num):
        qid = binascii.b2a_hex(data[:12])
        q_len = struct.unpack('>I', data[12:16])[0]
        q_content = data[16: 16 + q_len].decode('utf-16-be')
        a_opt = struct.unpack('>H', data[16 + q_len: 18 + q_len])[0]
        a_len = struct.unpack('>I', data[18 + q_len: 22 + q_len])[0]
        a_content = data[22 + q_len: 22 + q_len + a_len].decode('utf-16-be')
        question_list.append([qid, q_len, q_content, a_opt, a_len, a_content])
        data = data[22 + q_len + a_len:]
    return title_len, title, answer_num, question_list


def unpack_medal_group():
    # FIXME 腕表勋章墙指令
    pass


unpack_handler = {
    '\x01': unpack_login,
    '\x02': lambda data: '',
    '\x03': lambda data: struct.unpack('>Ii', data),
    '\x04': lambda data: '',
    '\x05': lambda data: '',
    '\x06': unpack_group_contact_diff,
    '\x07': lambda data: '',
    '\x08': lambda data: '',
    '\x0a': lambda data: '',
    '\x0b': lambda data: '',
    '\x0c': unpack_group_message,
    '\x0e': lambda data: struct.unpack('>HH', data),
    '\x10': lambda data: '',
    '\x12': lambda data: '',
    '\x14': lambda data: '',
    '\x16': unpack_monitor,
    '\x17': lambda data: '',
    '\x18': lambda data: '',
    '\x1a': lambda data: '',
    '\x1b': lambda data: '',
    '\x1c': lambda data: '',
    '\x1d': lambda data: '',
    '\x1e': unpack_watch_alarm,
    '\x1f': lambda data: '',
    '\x20': unpack_send_story,
    '\x22': unpack_delete_story,
    '\x24': lambda data: struct.unpack('>I', data),
    '\x26': unpack_a_key_call,
    '\x28': unpack_almanac,
    '\x29': lambda data: '',
    '\x31': unpack_almanac,
    '\x33': lambda data: '',
    '\x34': lambda data: '',
    '\x35': lambda data: '',
    '\x36': lambda data: struct.unpack('>B', data),
    '\x37': lambda data: '',
    '\x38': unpack_group_message,
    '\x3a': lambda data: '',
    '\x3c': lambda data: '',
    '\x3d': lambda data: '',
    '\x3f': lambda data: '',
    '\x40': unpack_lbs_faceback,
    '\x41': unpack_bluetooth,
    '\x42': unpack_bluetooth,
    '\x43': lambda data: '',
    '\x44': unpack_answer_game,
    '\x45': lambda data: '',
    '\x46': lambda data: struct.unpack('>I', data),
    '\x48': lambda data: data.decode('utf-16-be'),
    '\x4a': unpack_medal_group,
    '\x4b': lambda data: '',
}


def unpack_data(itype, data):
    return unpack_handler[itype](data)


def hex_format(s):
    ss = ''
    for i in s:
        h = hex(ord(i)).replace('0x', '')
        ss += h if len(h) == 2 else '0' + h
    return ss


class Emulate(object):
    def __init__(self, host='127.0.0.1', port=8000, imei=355372020827303, heartbeat=300, customer_id=0):
        self.address = (host, port)
        self.imei = imei
        self.imsi = 460001515535328
        self.mac = 'c4544458cb7a'
        self.heartbeat = heartbeat
        self.software_v = 20160408
        self.bluetooth_v = 20160408
        self.customer_id = customer_id
        self._sock = None
        self._queue = Queue.Queue()
        self.loop_started = 0
        self._last_info = (None, None)
        self.connect()
        self.login()

    def connect(self):
        self._sock = socket.socket()
        self._sock.connect(self.address)
        return self._sock

    def login(self):
        self.send('\x01', [self.imei, self.imsi, self.mac, self.heartbeat, self.software_v, self.bluetooth_v,
                           self.customer_id])

    def send(self, itype, params, ident=None):
        if ident is None:
            ident = struct.pack('>H', random.randint(0, 65535))
        if self.loop_started:
            self._queue.put((ident, itype, params))
        else:
            self._sock.send(pack_data(ident, itype, params))

    def _send(self):
        while True:
            data = self._queue.get()
            if not data:
                return None
            ident, itype, params = data
            self._sock.send(pack_data(ident, itype, params))

    def recv(self):
        data = self._sock.recv(8)
        if not data:
            raise socket.error
        version, ident, itype, length = struct.unpack('>B2s1sI', data)
        if length:
            data = self._sock.recv(length)
            if not data:
                raise socket.error
            return version, ident, itype, length, data
        else:
            return version, ident, itype, length, ''

    def heartbeat_loop(self):
        while 1:
            time.sleep(self.heartbeat)
            self.send('\x03', [])

    def _loop(self):
        send_thread = threading.Thread(target=self._send)
        send_thread.daemon = True
        send_thread.start()
        self.loop_started = 1
        try:
            while 1:
                self.action()
        except socket.error:
            print('%s socket terminate' % datetime.datetime.now())
        finally:
            self._queue.put(None)

    def loop(self, block=True):
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        if block:
            self._loop()
        else:
            recv_thread = threading.Thread(target=self._loop)
            recv_thread.daemon = True
            recv_thread.start()

    def locate(self, cells=None, gps=None, Ltype=1):
        if not cells:
            cells = []
        if not gps:
            lon = 0
            lat = 0
        else:
            lon, lat = gps
        self.send('\x05', [Ltype, lon, lat, len(cells), cells, time.time()])

    def action(self):
        version, ident, itype, length, data = self.recv()
        print('%s 0x%02x %r' % (datetime.datetime.now(), ord(itype), unpack_data(itype, data)))

        self._last_info = (itype, ident)

        method = getattr(self, 'action_0x%02x' % ord(itype), None)
        if method:
            method()
        elif ord(itype) % 2 == 0:
            self.react()

    def react(self):
        itype, ident = self._last_info
        if itype and ident:
            self.send(itype, [], ident=ident)

    def action_0x14(self):
        self.react()

        global n
        if n % 2 == 0:
            # 广东省广州市天河区科智路靠近科城大厦
            # self.locate(gps=(113.4395958, 23.1659372), Ltype=2)
            # self.locate([[460, 0, 9475, 44901, -78]
            #                 , [460, 0, 9475, 17252, -87]], Ltype=2)
            # 广东省广州市天河区天园街道华建大厦
            # self.locate([[460, 1, 9493, 7692, 51], [460, 1, 9493, 41232, 32], [460, 1, 9493, 7691, 32],
            #              [460, 1, 9493, 7693, 27], [460, 1, 9493, 5192, 22], [460, 1, 9493, 41241, 21],
            #              [460, 1, 9493, 41231, 21]], Ltype=2)
            self.locate(gps=(113.356512, 23.13408), Ltype=2)
        else:
            # 广东省广州市黄埔区揽月路靠近最牛的牛杂
            # self.locate([[460, 0, 9475, 61009, -59], [460, 0, 9475, 21855, -77]
            #                 , [460, 0, 9475, 18671, -84]
            #                 , [460, 0, 9475, 26963, -87]
            #                 , [460, 0, 9475, 50168, -91]
            #                 , [460, 0, 10331, 58526, -97]], Ltype=2)
            # 广东省广州市天河区天园街道天河公园
            self.locate(gps=(113.357234, 23.131497), Ltype=2)
        n += 1

    def action_0x08(self):
        # self.login()
        self.react()


n = 0


@click.command()
@click.option('-h', '--host', default='127.0.0.1', help='server host')
@click.option('-p', '--port', default=8000, help='server port')
@click.option('--imei', default=0, help='emulate imei')
@click.option('--debug/--no-debug', default=False, help='connect to the "ios16.com"')
@click.option('--produce/--no-produce', default=False, help='connect to the "mobilebrother.net"')
@click.option('-id', '--customer', default=0, help='emulate customer id')
def main(host, port, imei, debug, produce, customer):
    if debug:
        if host == '127.0.0.1':
            host = 's.ios16.com'
        if imei is 0:
            imei = 325732545250001
    elif produce:
        if host == '127.0.0.1':
            host = 's.mobilebrother.net'
        if imei is 0:
            imei = 325732545250001
        if customer is 0:
            customer = 100
    elif imei is 0:
        imei = 355372020827303
    emulate = Emulate(host=host, port=port, imei=imei, customer_id=customer)

    # emulate.locate([[460, 0, 9475, 44901, -78], [460, 0, 9475, 17252, -87]])  # 科学城
    # emulate.locate(gps=(113.4395958, 23.1659372), Ltype=2)  # 科学城
    # emulate.send('\x29', ['56909c5f0bdb823db41496a8'])

    # def test():
    #     time.sleep(3)
    #     emulate.send('\x33', [])
    # threading.Thread(target=test).start()

    # emulate.send('\x1f', ['18028577812', 'hello sms\x00'])

    # emulate.send('\x43', ['c4544458cb7a'])

    # t = threading.Thread(target=emulate_locate, args=(emulate,))
    # t.setDaemon(True)
    # t.start()
    # emulate.locate(gps=(113.339682, 23.134835), Ltype=2)
    # emulate.locate(gps=(113.338888, 23.134519), Ltype=2)
    # emulate.locate(gps=(113.337922, 23.134204), Ltype=2)

    # emulate.send('\x31', [])
    # emulate.send('\x45', [time.time(), time.time(), [
    #    # ['5721d0328df9ea5d0cc749de', 1, 1],
    #    # ['5721d07f8df9ea5d0cc749e2', 2, 1],
    #    # ['5721d0918df9ea5d0cc749e4', 2, 0],
    #    # ['5721cfc88df9ea5d0cc749db', 1, 1],
    #     ['5721cfbe8df9ea5d0cc749da', 1, 1],
    #     ['5721d0458df9ea5d0cc749e0', 2, 0],
    #     ['5721d0b48df9ea5d0cc749e8', 2, 1],
    #     ['5721d0918df9ea5d0cc749e4', 1, 1],
    # ]])
    # emulate.send('\x41', [])

    emulate.loop()


if __name__ == '__main__':
    main()
