# coding: utf-8
"""
script to send email daily about the grap user info in MySQL grapuser_info table
"""

import MySQLdb
import common
from prettytable import PrettyTable

sql_config = {
    'host': "10.4.14.233",
    'user': "tuike",
    'passwd': "sv8VW6VhmxUZjTrU",
    'db': 'tuike',
    'charset': 'utf8'
}

# sql_config = {
#     'host': "localhost",
#     'user': "testuser",
#     'passwd': "",
#     'db': 'tuike',
#     'charset': 'utf8'
# }

def grap_info():
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql = """ select grap_source, user_name, account_mark, buy_num, pub_num, expire_time
 from grapuser_info where account_type = '购买账号' """
    cursor.execute(sql)
    data = cursor.fetchall()
    x = PrettyTable(['来源', '用户名', '地区', '购买余额', '发布余额', '过期时间'])
    for i in data:
        x.add_row(i)
    # print x
    # print x
    return x.get_html_string(sortby=u"购买余额").encode('utf8')


def eformat(html):
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
    msg = msg_head + """<h2>简历下载账号信息</h2>"""
    msg2 = grap_info()
    msg = msg + msg2 + "</body></html>"
    msg = msg.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
    # print msg
    return msg


if __name__ == '__main__':
    data =grap_info()
    msg = eformat(data)
    common.sendEmail('main', '简历渠道账号信息', msg, msg_type=1, des= 'op')