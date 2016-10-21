# -*- coding: utf-8 -*-
"""
执行gps策略的loop
"""
import gevent
import datetime
import time
import setting
from pymongo.cursor import CursorType
from agent.client import Demand
from core.db import db
from strategy import TestStrategy, get_diff_second

agent = Demand(setting.broker['host'], setting.broker['request_port'])

TaskingWatch = {}


def get_task_data_list(page, num):
    if not page and not num:
        return TaskingWatch.viewkeys()
    return [{
                'imei': task.imei,
                'strategy': task.strategy,
                'status': task.status + task.del_status,
            } for task in TaskingWatch.values()[page * num: (page + 1) * num]]


def get_task_total():
    return len(TaskingWatch)


def add_task(imei, gps_strategy):
    if imei not in TaskingWatch:
        gevent.spawn(gps_strategy_handle, imei, gps_strategy)
    else:
        task = TaskingWatch[imei]
        task.runing = 1
        task.del_status = ''


def del_task(imei):
    if imei in TaskingWatch:
        task = TaskingWatch[imei]
        task.runing = 0
        task.del_status = ',(%s) delete' % datetime.datetime.now()


def gps_strategy_handle(imei, strategy):
    """
    针对每个腕表执行gps策略
    except错误由外层捕获
    只处理TaskingWatch字典键值
    """
    try:
        task = TestStrategy(imei)
        TaskingWatch[imei] = task
        task.join()
        if task.runing:
            # 腕表策略还未结束,在晚上 9 点关机腕表
            now = datetime.datetime.now()
            t = time.localtime()
            power_time = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, 21, 0)
            if now < power_time:
                second = get_diff_second(power_time, now)
                task.status = '(%s) wait %s to close' % (now, second)
                gevent.sleep(second)
            agent.send(imei, '\x34', '')
    finally:
        del TaskingWatch[imei]


def gps_strategy_loop():
    while 1:
        for watch in db.watch.find({'gps_strategy': 'test'}, {'gps_strategy': 1}, cursor_type=CursorType.EXHAUST):
            if watch['_id'] not in TaskingWatch:
                gevent.spawn(gps_strategy_handle, watch['_id'], watch['gps_strategy'])
        gevent.sleep(300)
