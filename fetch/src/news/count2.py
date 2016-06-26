# coding: utf8

import sqlite3
import MySQLdb
import common
import datetime
from prettytable import PrettyTable
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# sql_config = {
#     'host': "localhost",
#     'user': "testuser",
#     'passwd': "",
#     'db': 'tuike',
#     'charset': 'utf8',
# }

sql_config = {
    'host': "10.4.14.233",
    'user': "tuike",
    'passwd': "sv8VW6VhmxUZjTrU",
    'db': 'tuike',
    'charset': 'utf8',
}
# db = sqlite3.connect('test.db')

time_str = datetime.datetime.now() - datetime.timedelta(days=3)
print time_str.strftime('%Y-%m-%d')


def source_list():
    sql_sr = 'select DISTINCT `source` from news_info '
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    cursor.execute(sql_sr)
    data_sr = cursor.fetchall()
    db.close()
    sr_list = []
    for i in data_sr:
        sr_list.append(i[0])
    return sr_list

def cnb_count():
    sql_cnb = "select count(id) from news where source like 'cnblog_%'"
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    cursor.execute(sql_cnb)
    data_cnb = cursor.fetchall()
    count_cnb = data_cnb[0][0]
    db.close()
    return count_cnb

def table_cr(source):
    sql_1 = 'select `name` from news_info where `source` = "{}"  and `interval` != 0 '.format(source)
    print sql_1
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    cursor.execute(sql_1)
    data = cursor.fetchall()
    table_list = []
    for i in data:
        table_list.append(i[0])
    db.close()
    return table_list

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def to_pass():
    stat_list = []
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    time_to = datetime.datetime.today().strftime('%Y-%m-%d')
    time_yes = (datetime.datetime.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    sql_pass = "select `id` from news where date(`pub_time`) = '{}' ".format(time_yes)
    sql_to = "select `id` from news where date(`pub_time`) = '{}' ".format(time_to)
    cursor.execute(sql_pass)
    data_pass = cursor.fetchall()
    cursor.execute(sql_to)
    db.close()
    data_to = cursor.fetchall()
    return len(data_pass), len(data_to)

def to_pass2():   # add_time 这两天更新的量
    stat_list = []
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    time_to = datetime.datetime.today().strftime('%Y-%m-%d')
    time_yes = (datetime.datetime.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    sql_pass = "select `id` from news where date(`add_time`) = '{}' ".format(time_yes)
    sql_to = "select `id` from news where date(`add_time`) = '{}' ".format(time_to)
    cursor.execute(sql_pass)
    data_pass = cursor.fetchall()
    cursor.execute(sql_to)
    db.close()
    data_to = cursor.fetchall()
    return len(data_pass), len(data_to)

def dict_list():
    sql_1 = 'select `name`, `nameCN` from news_info  '
    print sql_1
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    cursor.execute(sql_1)
    data = cursor.fetchall()
    db.close()
    dict_list = {}  # name 对应的中文解释，字典列表
    for i in data:
        dict_list.update({i[0]: i[1]})
    return dict_list

def big_cr(table_list):
    big_dict = Vividict()
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    for i in table_list:
        sql_2 = "select distinct(date(pub_time)) from news where source = '{}' and pub_time > '{}'".format(i, time_str)
        # print sql_2
        cursor.execute(sql_2)
        data2 = cursor.fetchall()
        # print data
        date_list = []
        for i2 in data2:
            date_list.append(i2[0])
        stat_dict = {}
        for i3 in date_list:
            sql_3 = "select `id` from news where date(`pub_time`) = '{}' and source = '{}' ".format(i3, i)
            cursor.execute(sql_3)
            data3 = cursor.fetchall()
            big_dict[i][i3.strftime('%Y-%m-%d')] = len(data3)
    cursor.close()
    return big_dict

def total_00(m_type):   # 统计不同来的总数
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql_11 = "select `name` from news_info where `type` = '{}'".format(m_type)
    cursor.execute(sql_11)
    data_11 = cursor.fetchall()
    list_11 = []
    total_11 = 0
    for i11 in data_11:
        list_11.append(i11[0])
    for i111 in list_11:
        sql_111 = """select count(id) from news where `source` = '{}'""".format(i111)
        cursor.execute(sql_111)
        data_111 = cursor.fetchall()
        total_11 += data_111[0][0]
    db.close()
    return total_11


def html_cr(big_dict):
    html = u'''
        <table><tbody><tr>
        <th>source</th>
        <th>all</th>
        <th>time</th>
        <th>num</th>
    </tr>'''
    for i_0 in sorted(big_dict.keys()): #msgtype
        html_line = '<tr>'
        html_line += '<td rowspan="{}" >'.format(len(big_dict[i_0])) + dict_list[i_0] + '</td>'
        c_sum = 0
        for i_1 in sorted(big_dict[i_0].keys()):
            c_sum += big_dict[i_0][i_1]
        html_line += '<td rowspan="{}" >'.format(len(big_dict[i_0])) + str(c_sum) + '</td>'
        c3 = 1
        for i_1 in sorted(big_dict[i_0].keys(), reverse=True): # ext1
            if c3 != 1:
                html_line += '<tr>'
            c3 += 1
            html_line += '<td>' + i_1 + '</td>' + '<td>' + str(big_dict[i_0][i_1]) + '</td></tr>'
        html += html_line
    html += '</tbody></table>'
    html = html.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
    # print msg
    return html



def no_list(list_d):
    # 找出在 news info 的最后抓取时间，和评论
    xx = PrettyTable(["英文id","中文","来源","最后一次成功数量","最后成功抓取时间","最后一次页面数量","最后一次页面更新数量","最后一次抓取时间","备注"])
    xx.align["英文id"] = "l"
    for iii in list_d:
        print iii
        sql_d = """ select `name`, `nameCN`, `source`, `latest_num`, `latest_time`, `latest_total`, `latest_num2`, `update_time`,
        `comment` from news_info WHERE `name` = '{}' and `interval` != 0 """.format(iii)
        db = MySQLdb.connect(**sql_config)
        cursor = db.cursor()
        cursor.execute(sql_d)
        data_d = cursor.fetchall()
        db.close()
        try:
            xx.add_row(data_d[0])
        except:
            pass
    print xx.get_string(sortby=u'最后一次页面数量').encode('utf8')
    return xx.get_html_string(sortby=u'最后一次页面数量')

def tm_compare(time1, time2):
    try:
        if time1 - time2 > datetime.timedelta(hours=1):
            return True
        else:
            return False
    except Exception, e:
        print e
        return False

def no_list2(list_d):  # 红色显示当rss有更新，但是， 成功入库的时间不等于抓取时间
    html = u''' <br> 标红为有新增内容但是成功抓取时间不等于更新时间的<br>
        <table><tbody><tr>
        <th>英文id</th>
        <th>中文</th>
        <th>来源</th>
        <th>最后一次成功数量</th>
        <th>最后成功抓取时间</th>
        <th>最后一次页面数量</th>
        <th>最后一次页面更新量</th>
        <th>最后一次抓取时间</th>
        <th>备注</th>
    </tr>'''
    print list_d
    ll = []
    for iii in list_d:
        print iii
        sql_d = """ select `name`, `nameCN`, `source`, `latest_num`, `latest_time`, `latest_total`, `latest_num2`, `update_time`,
        `comment` from news_info WHERE `name` = '{}' and `interval` != 0 """.format(iii)
        db = MySQLdb.connect(**sql_config)
        cursor = db.cursor()
        cursor.execute(sql_d)
        data_d = cursor.fetchall()
        db.close()
        # print data_d
        res_p = data_d[0]
        ll.append(res_p)
    ll2 = sorted(ll, key=lambda b: b[5])
    for res in ll2:
        try:
            # res = data_d[0]
            # res = sorted(res, key=lambda b: b[5])
            if (int(res[6]) > 0 and tm_compare(res[4], res[7])) or int(res[5]) == 0:
                html += '<tr style="color:red">'
            else:
                html += '<tr>'
            for i in res:
                    html += '<td>' + str(i) + '</td>'
            html += '</tr>'
        except Exception, e:
            print e
            pass
    html += '</tbody></table>'
    html = html.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
    return html.encode('utf8')
# html_no = u'<br>一天没更新<br>' + no_list(list_1d2) + u'<br>三天没更新<br>' + no_list(list_3d2) + \
#     u'<br>一周没更新<br>' + no_list(list_7d2)

# html_no = u'<br>hello<br>' + no_list(sr_list) + u'<br>'

def stop_list():  # 返回不抓的表格
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql = """select `name`, `nameCN`, `source`, `interval`, `comment` from news_info where `source` = 'Blog'"""
    cursor.execute(sql)
    data_d = cursor.fetchall()
    xx = PrettyTable(["英文id","中文","来源","间隔","备注"])
    xx.align["英文id"] = "l"
    html = "<br> 目前停止抓取的来源, 类型为 blog 的 每月15号提醒一次确定停止抓取的来源(interval =0)<br>"
    for i in data_d:
        try:
            xx.add_row(i)
        except Exception, e:
            print e
    to_int = datetime.datetime.now().day
    if to_int == 15:
        sql2 = """select `name`, `nameCN`, `source`, `interval`, `comment` from news_info where `interval` = 0 """
        cursor.execute(sql2)
        data_d2 = cursor.fetchall()
        for i in data_d2:
            try:
                xx.add_row(i)
            except Exception, e:
                print e
    db.close()
    html += xx.get_html_string(sortby=u'来源') + '<br><br>'
    html = html.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
    return html


def main():
    sr_list = source_list()
    html = ''
    for i in sr_list:
        # html_i = '<br>' + i + '</br>'
        table_list = table_cr(i)
        # big_dict = big_cr(table_list)
        html_i = '<br>' + i + '</br>' + no_list2(table_list)
        html += html_i
    html = html.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")

    msg_style = """<style type="text/css">
    .body{
    font-family: Monaco, Menlo, Consolas, "Courier New", "Lucida Sans Unicode", "Lucida Sans", "Lucida Console",  monospace;
    font-size: 14px;
    line-height: 20px;
    }

    .table{ border-collapse:collapse; border:solid 1px gray; padding:6px}
    .table td{border:solid 1px gray; padding:6px}

    .color-ok {color: green;}
    .color-warning {color: coral;}
    .color-error {color: red;}

    .bg-ok {background-color: lavender;}
    .bg-warning {background-color: yellow;}
    .bg-error {background-color: deeppink;}
    </style>"""
    msg_head = """<html><head><meta charset="utf-8"></head>""" + msg_style + "<body>"
    msg = msg_head  # + u"""<h2>资讯来源报表，只展示4天内的情况，表格中的时间是文章发布时间</h2>"""
    data_pass, data_to = to_pass2()
    count_cnb = cnb_count()
    # data_pass, data_to = 0, 0
    msg += u"<br>昨天抓取的文章总量： " + str(data_pass) + u"； 今天抓取的文章总量：　" + str(data_to) + ' 这两个是抓取时间，遍历20W的发布时间太慢了<br>' + \
           u" 资讯类数据总量： " + str(total_00(1)) + '<br>' + u"  博客类数据总量： " + str(total_00(2)) + '<br>' +\
           u" 微信总量： " + str(total_00(3)) + '<br>' + \
           u"<br> cnblog总数（单独抓历史文章）： " + str(count_cnb) + u" （暂时分4类，分类可以加多，news_info表 type 字段）<br>"
    stop_l = stop_list()
    msg = msg + stop_l + html + "</body></html>"
    msg = msg.encode('utf8')
    common.sendEmail(title='资讯抓取报表', message=msg)


if __name__ == '__main__':
    # table_cr(source_list()[1])
    main()
