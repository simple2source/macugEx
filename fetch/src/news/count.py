# coding: utf8

import sqlite3
import MySQLdb
import common
import datetime
from prettytable import PrettyTable

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

db = MySQLdb.connect(**sql_config)
cursor = db.cursor()

sql_sr = 'select DISTINCT `source` from news_info '
cursor.execute(sql_sr)
data_sr = cursor.fetchall()
db.close()
sr_list = []
for i in data_sr:
    sr_list.append(i[0])

sql_cnb = "select count(id) from news where source like 'cnblog_%'"
db = MySQLdb.connect(**sql_config)
cursor = db.cursor()
cursor.execute(sql_cnb)
data_cnb = cursor.fetchall()
count_cnb = data_cnb[0][0]
db.close()

def table_cr(source):
    sql_1 = 'select `name` from news_info where `source` = "{}" '.format(source)
    print sql_1
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    cursor.execute(sql_1)
    data = cursor.fetchall()
    db.close()
    table_list = []
    for i in data:
        table_list.append(i[0])
    return table_list


time_str = datetime.datetime.now() - datetime.timedelta(days=3)
print time_str.strftime('%Y-%m-%d')
print type(time_str)
# print time_str.isoformat()
# quit()

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

db = MySQLdb.connect(**sql_config)
cursor = db.cursor()
stat_list = []
time_to = datetime.datetime.today().strftime('%Y-%m-%d')
time_yes = (datetime.datetime.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
sql_pass = "select `id` from news where date(`pub_time`) = '{}' ".format(time_yes)
sql_to = "select `id` from news where date(`pub_time`) = '{}' ".format(time_to)

cursor.execute(sql_pass)
data_pass = cursor.fetchall()
cursor.execute(sql_to)
data_to = cursor.fetchall()
db.close()
# print data_pass
print len(data_pass)
# print data_to
print len(data_to)

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
# print dict_list

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
            # print sql_3
            cursor.execute(sql_3)
            data3 = cursor.fetchall()
            # print data3, len(data3)
            # print 'weichat_id  {} date {} had published {} articles '.format(i, i3, len(data3))
            # stat_dict['source']
            big_dict[i][i3.strftime('%Y-%m-%d')] = len(data3)
    db.close()
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

html = ''
for i in sr_list:
    # html_i = '<br>' + i + '</br>'
    table_list = table_cr(i)
    big_dict = big_cr(table_list)
    html_i = '<br>' + i + '</br>' + html_cr(big_dict)
    html += html_i


db = MySQLdb.connect(**sql_config)
cursor = db.cursor()
sql_1d = """ select DISTINCT `source` from news where date(`pub_time`) = '{}' """.format(time_to)
time_str3 = datetime.datetime.now().date() - datetime.timedelta(days=3)
time_str7 = datetime.datetime.now().date() - datetime.timedelta(days=7)
sql_3d = """ select DISTINCT `source` from news  where `pub_time` > '{}' """.format(time_str3)
sql_7d = """ select DISTINCT `source` from news  where `pub_time` > '{}' """.format(time_str7)
print sql_1d
print sql_3d
print sql_7d
cursor.execute(sql_1d)
data_1d = cursor.fetchall()
cursor.execute(sql_3d)
data_3d = cursor.fetchall()
cursor.execute(sql_7d)
data_7d = cursor.fetchall()
list_1d = [x[0] for x in data_1d ]
list_3d = [x[0] for x in data_3d ]
list_7d = [x[0] for x in data_7d ]
all_list = [x for x in dict_list]

list_1d2 = set(all_list) ^ set(list_1d)
list_3d2 = set(all_list) ^ set(list_3d)
list_7d2 = set(all_list) ^ set(list_7d)

# print list_1d2
# print list_3d2
# print list_7d2

def no_list(list_d):
    # 找出在 news info 的最后抓取时间，和评论
    xx = PrettyTable(["英文id","中文","来源","最后一次数量","最后抓取时间","备注","最后发布时间"])
    xx.align["英文id"] = "l"
    for iii in list_d:
        # print iii
        sql_d = """ select `name`, `nameCN`, `source`, `latest_num`, `latest_time`, `comment` from news_info WHERE
        `name` = '{}' """.format(iii)
        sql_d2 = """select max(`pub_time`) from news where `source` = '{}' """.format(iii)
        cursor.execute(sql_d)
        data_d = cursor.fetchall()
        cursor.execute(sql_d2)
        data_d2 = cursor.fetchall()
        try:
            pub_time = data_d2[0][0]
        except:
            pub_time = ''
        try:
            xx.add_row(data_d[0] + (pub_time,))
        except:
            pass
    print xx.get_string().encode('utf8')
    return xx.get_html_string()

html_no = u'<br>一天没更新<br>' + no_list(list_1d2) + u'<br>三天没更新<br>' + no_list(list_3d2) + \
    u'<br>一周没更新<br>' + no_list(list_7d2)

html_no = html_no.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")

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
msg = msg_head + u"""<h2>资讯来源报表，只展示4天内的情况，表格中的时间是文章发布时间</h2>"""

msg += u"<br>昨天发布的文章总量： " + str(len(data_pass)) + u"； 今天发布的文章总量：　" + str(len(data_to)) + '<br>' + \
       u"资讯类数据总量： " + str(total_00(1)) + u"  博客类数据总量： " + str(total_00(2)) + \
       u"微信总量： " + str(total_00(3)) + \
       u"<br>cnblog总数（单独抓历史文章）： " + str(count_cnb) + u" （暂时分3类，分类可以加多，news_info表 type 字段）<br>"
msg = msg + html + html_no + "</body></html>"
msg = msg.encode('utf8')

common.sendEmail(title='资讯抓取报表', message=msg)
