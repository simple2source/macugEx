# encoding: utf8

import requests
import logging, logging.config
import time
import common, json, os, MySQLdb
import timeit
import redispipe
import random
import sys
from prettytable import PrettyTable
import datetime
import re

rp = redispipe.Rdsreport()
common.log_init(__name__, 'test.log')
web_dict = {
    'translate': {'url': 'http://123.58.136.243:8087/translator',
                  'data': {},
                  'op': 'get'},
    'segmenter': {'url': 'http://123.58.136.243:8087/segmenter',
                 'data': {'text': '没时间解释了，赶紧上车'},
                 'op': 'get'},
    'worktile_task': {'url': 'http://123.58.128.216:8086/task/',
                      'data': {'q': 'asdfa', 'from': '1223', 'size': 10},
                      'op': 'get'},
    'transfer_51': {'url': 'http://123.58.128.216:8086/job51/',
                    'data': {'page': random.choice(range(1, 10)),
                             'area': random.choice([u'广州', u'深圳', u'北京', u'上海']),
                             'degree': u'本科',
                             'keyword': random.choice(['java', 'php', 'ios']),
                             'industry': u'计算机软件'},
                    'op': 'get'},
    'transfer_zl': {'url': 'http://123.58.128.216:8086/zhilian/',
                    'data': {'page': random.choice(range(1, 9)),
                             'area': random.choice([u'广州', u'深圳', u'北京', u'上海']),
                             'degree': '2,7',
                             'keyword': random.choice(['java', 'php', 'ios']),
                             'year': '3,99'},
                    'op': 'get'},
    'transfer_cjol': {'url': 'http://123.58.128.216:8086/cjol/',
                    'data': {'page': random.choice(range(1, 4)),
                             'area': random.choice([u'广州', u'深圳', u'北京', u'上海']),
                             'degree': '60',
                             'keyword': random.choice(['java', 'php', 'ios']),
                             'industry': u'计算机软件'},
                    'op': 'get'},

}


def web_test(name, url, op, data=None):
    if data is None:
        data = dict()
    s = requests.Session()
    start = time.clock()
    start2 = timeit.default_timer()
    start3 = time.time()
    if op == 'get':
        r = s.get(url, params=data, timeout=15)
    elif op == 'post':
        r = s.post(url, data=data, timeout=15)
    else:
        logging.error('invalid http method')
    logging.info('test url is {}'.format(r.url))
    end = time.clock()
    stop3 = time.time()
    stop2 = timeit.default_timer()
    logging.info('timeit {}'.format(stop2 - start2))
    logging.info('time.time {}'.format(stop3 - start3))
    resp = r.status_code
    logging.info('response time time clock is {}'.format(end-start))
    resp_time = stop2 - start2
    if resp < 299:
        # do redis
        logging.info('url {} works normal, status_code is {}'.format(url, resp))
    else:
        logging.error('http code error code is {}'.format(resp))
        common.sendEmail(title='{} auto test get err code {}'.format(name, resp), 
                         message='RT, Web api test error, url is {}, code {}, time is {}'.format(url, resp, resp_time))

    return resp, resp_time


def run_test(dd):
    """读取字典（msgtype, url) 来测试"""
    for i in web_dict:
        resp, resp_time = web_test(i, web_dict[i]['url'], op=web_dict[i].get('op', 'get'), data=web_dict[i].get('data', {}))
        rp.tranredis(msgtype=i, num=0, ext1=resp_time, ext2=resp)


def sql_related():
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    today = str(datetime.datetime.today().date())
    x = PrettyTable([u'统计项', u'响应代码', u'次数', u'平均值', u'最大值', u'最小值'])
    x.align[u"统计项"] = "l"
    x.border = True
    html = '''<br><br><h2>api 测试</h2><br>
        <table><tbody><tr>
        <th>msgtype</th>
        <th>响应代码</th>
        <th>次数</th>
        <th>平均</th>
        <th>最大</th>
        <th>最小</th>
    </tr>'''
    for i in web_dict:
        sql = """select distinct(ext2), count(ext2),  avg(ext1), max(ext1), min(ext1) from stats
            where msgtype = '{}' and date(stat_time) = '{}' group by ext2""".format(i, today)
        cursor.execute(sql)
        data = cursor.fetchall()
        html += '<tr>' + '<td rowspan="{}" >'.format(len(data)) + i + '</td>'

        for k in data:
            if not k[0].startswith('2'):
                html += '<td style="color:red">' + k[0] + '</td>'
            else:
                html += '<td>' + k[0] + '</td>'
            html += '<td>' + str(k[1]) + '</td>'
            for j in k[2:]:
                if float(j) > 5:
                    html += '<td style="color:red">' + str(j) + '</td>'
                else:
                    html += '<td>' + str(j) + '</td>'
            html += '</tr>'
            # html += '<td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            #     str(k[1]), str(k[2]), str(k[3]), str(k[4]))
            x.add_row([i, k[0], k[1], k[2], k[3], k[4]])
    html += '</tbody></table>'
    print x.get_string().encode('utf8')
    return html.encode('utf8')


def res_email():
    msg_style = '''<html>
    <head>
        <meta charset="utf-8">
    </head>
    <style type="text/css">

    .body{
      font-family: Monaco, Menlo, Consolas, "Courier New", "Lucida Sans Unicode", "Lucida Sans", "Lucida Console",  monospace;
      font-size: 14px;
      line-height: 20px;
    }

    .table{ border-collapse:collapse; border:solid 1px gray; }
    .table td{border:solid 1px gray; padding:6px;}

    .color-ok {color: green;}
    .color-warning {color: coral;}
    .color-error {color: red;}

    .bg-ok {background-color: lavender;}
    .bg-warning {background-color: yellow;}
    .bg-error {background-color: deeppink;}
    </style>

    <body class="body">
    <h2>web api 在线监控报表, 监控每5分钟跑一次</h2>'''
    msg = sql_related()
    msg = msg_style + msg + "<br><br>2开头是正常的<br><br>"
    msg += '</body>' + '</html>'
    msg = msg.replace('<table>', '<table class="table">').replace('<th>', "<th class='table'>")
    common.sendEmail(title='web api 在线监控报表', message=msg)



def get_conf(self):
    """从MySQL里读取配置，检查时间，每5分钟更新一次"""
    try:
        db = MySQLdb.connect(**self.sql_config)
        cursor = db.cursor()
        sql = """select `msgtype`, `interval` from stats_info"""
        cursor.execute(sql)
        data = cursor.fetchall()
        d = dict()
        for msgtype, interval in data:
            d[msgtype] = interval
        # d['_expired_time'] = datetime.datetime.now() + datetime.timedelta(minutes=self.config_expired_minutes)
        logging.info('get conf from mysql success conf is {}'.format(d))
        return d
    except Exception as e:
        logging.error('cannot update config from mysql, err msg is {}'.format(e), exc_info=True)
        return None


if __name__ == '__main__':
    if len(sys.argv) == 1:
        run_test(web_dict)
    else:
        res_email()
