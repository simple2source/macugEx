# -*- coding: utf-8 -*-
"""
腕表gps策略模块
"""
try:
    import ujson as json
except ImportError:
    import json

import datetime
import time
import gevent
import setting
from core.db import db, redis
from agent.client import Demand, OK

agent = Demand(setting.broker['host'], setting.broker['request_port'])


def request_watch_gps_logging(imei, gps_open=True):
    if gps_open:
        result = agent.send(imei, '\x36', '\x02')
        if result == OK:
            db.watch_gps_loger.insert_one({
                'imei': imei,
                'status': 'request',
                'timestamp': time.time(),
                'recv_timestamp': 0
            })
            redis.hset('Watch:%s' % imei, 'gps_logging', 1)
    else:
        result = agent.send(imei, '\x36', '\x01')
        if result == OK:
            db.watch_gps_loger.insert_one({'imei': imei, 'status': 'close', 'timestamp': time.time()})


def get_diff_second(datetime1, datetime2):
    return (datetime1 - datetime2).total_seconds()


class TestStrategy(object):
    def __init__(self, imei):
        """
        腕表默认gps测试策略
        """
        self.imei = imei
        self.strategy = 'test'
        self.status = 'init'  # 腕表执行状态
        self.del_status = ''  # 腕表被删除状态
        self.runing = 1

    @property
    def start_time(self):
        localtime = time.localtime()
        year, month, day = localtime.tm_year, localtime.tm_mon, localtime.tm_mday
        return datetime.datetime(year, month, day, 8, 0)

    @property
    def finish_time(self):
        localtime = time.localtime()
        year, month, day = localtime.tm_year, localtime.tm_mon, localtime.tm_mday
        return datetime.datetime(year, month, day, 20, 30)

    @property
    def time_range(self):
        localtime = time.localtime()
        year, month, day = localtime.tm_year, localtime.tm_mon, localtime.tm_mday
        return [
            (datetime.datetime(year, month, day, 8, 0), datetime.datetime(year, month, day, 9, 20)),
            (datetime.datetime(year, month, day, 12, 30), datetime.datetime(year, month, day, 14, 00)),
            (datetime.datetime(year, month, day, 18, 30), datetime.datetime(year, month, day, 20, 30)),
        ]

    def check_time_in_range(self, sometime):
        """
        当前时间是否在策略时间段中
        """
        for start, end in self.time_range:
            if start <= sometime <= end:
                return True
        else:
            return False

    def get_near_time_second(self, sometime):
        """
        在策略时间段中,当前时间与最近的时间点之间的秒数
        或者当前时间与结束时间之间的秒数
        """
        detail_list = []
        for start, end in self.time_range:
            if sometime < start:
                detail_list.append(get_diff_second(start, sometime))
            elif sometime < end:
                detail_list.append(get_diff_second(end, sometime))
        if not detail_list:
            return get_diff_second(self.finish_time, sometime)
        return min(detail_list)

    def run(self):
        """
        腕表gps策略执行函数
        """
        # 开5分钟,关1分钟
        request_watch_gps_logging(self.imei)
        gevent.sleep(60)
        request_watch_gps_logging(self.imei)
        gevent.sleep(60)
        request_watch_gps_logging(self.imei)
        gevent.sleep(60)
        request_watch_gps_logging(self.imei)
        gevent.sleep(60)
        request_watch_gps_logging(self.imei)
        gevent.sleep(60)
        request_watch_gps_logging(self.imei, gps_open=False)
        gevent.sleep(60)

    def join(self):
        while self.runing:
            now = datetime.datetime.now()
            if now < self.finish_time:
                if not self.check_time_in_range(now):
                    if now >= self.finish_time:
                        self.status = 'finish'
                        break
                    second = self.get_near_time_second(now)
                    self.status = '(%s) sleep %ss' % (now, second)
                    gevent.sleep(second)
                    continue
                self.status = '(%s) runing' % now
                self.run()
            else:
                t = time.localtime()
                next_start_time = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, self.start_time.hour,
                                                    self.start_time.minute)
                second = get_diff_second(next_start_time, now)
                self.status = '(%s) will wait %s' % (now, second)
                gevent.sleep(second)
