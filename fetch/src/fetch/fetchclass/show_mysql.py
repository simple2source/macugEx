# coding=utf8

import os,sqlite3,datetime,time
from common import *
from prettytable import PrettyTable
import MySQLdb
import sys
import copy, re, pprint
reload(sys)
sys.setdefaultencoding('utf8')

week_str = (datetime.date.today()-datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def get_mysql(module_name, **kwargs):
    if len(kwargs) > 0:
        a = kwargs
        s = ""
        for i in a:
            s += """ and {} = "{}" """.format(i, a[i])
    else:
        s = ""

    # print kwargs
    db = MySQLdb.connect(**sql_config)
    cur = db.cursor()
    yesterday_str = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    today_str = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
    onehour_before = (datetime.datetime.now()-datetime.timedelta(seconds=3600)).strftime('%Y-%m-%d %H:%M:%S')
    fivemin_before = (datetime.datetime.now()-datetime.timedelta(seconds=300)).strftime('%Y-%m-%d %H:%M:%S')
    sql = """select sum(num) from stats WHERE msgtype = "{}" """.format(module_name) + s
    cur.execute(sql)
    total_num = cur.fetchall()[0][0]
    if not total_num:
        total_num = 0
    # print total_num
    sql_today = sql + """ and stat_time > "{}" """.format(today_str)
    cur.execute(sql_today)
    today_data = cur.fetchall()[0][0]
    if not today_data:
        today_data = 0
    # print today_data
    sql_yester = sql + """ and stat_time > "{}" and stat_time < "{}" """.format(yesterday_str, today_str)
    cur.execute(sql_yester)
    yester_data = cur.fetchall()[0][0]
    if not yester_data:
        yester_data = 0
    # print yester_data
    sql_hour = sql + """ and stat_time > "{}" """.format(onehour_before)
    cur.execute(sql_hour)
    hour_data = cur.fetchall()[0][0]
    if not hour_data:
        hour_data = 0
    # print hour_data
    sql_min  = sql + """ and stat_time > "{}" """.format(fivemin_before)
    cur.execute(sql_min)
    min_data = cur.fetchall()[0][0]
    if not min_data:
        min_data = 0
    # print min_data
    db.close()
    return [yester_data, today_data, hour_data, min_data]


def list_con(ex='ext1', msgtype='cjol'):
    """找ext1,2,3 独立的值"""
    sql = '''select distinct {} from stats where msgtype = '{}';'''.format(ex, msgtype)
    db = MySQLdb.connect(**sql_config)
    cur = db.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    db.close()
    l_list = []
    for l in data:
        l_list.append(l[0])
    return l_list


def c2_list(msgtype='cjol', ex='ext1', **kwargs):
    """返回ext1的值"""
    if len(kwargs) > 0:
        a = kwargs
        s = ""
        for i in a:
            s += """ and {} = "{}" """.format(i, a[i])
    else:
        s = ''
    sql = '''select distinct {} from stats where msgtype = '{}' and stat_time > '{}' '''.format(ex, msgtype, week_str) + s
    # print sql
    db = MySQLdb.connect(**sql_config)
    cur = db.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    db.close()
    l_list = []
    for l in data:
        l_list.append(l[0])
    return l_list


def c3_list(msgtype='cjol'):
    l_list = []
    # ex_list = ['ext1', 'ext2', 'ext3']
    # for ex in ex_list:
    list_1 = c2_list(msgtype, 'ext1')
    d = Vividict()
    for l_1 in list_1:
        list_2 = c2_list(msgtype, 'ext2', ext1=l_1)
        for l_2 in list_2:
            list_3 = c2_list(msgtype, 'ext3', ext1=l_1, ext2=l_2)
            for l_3 in list_3:
                l_list.append([msgtype, l_1, l_2, l_3])
                d[msgtype][l_1][l_2][l_3]={}
    # print d
    # pprint.pprint(d)
    return l_list, d


def c4_list():
    l = []
    m_list = msg_list()
    d = Vividict()
    for m in m_list:
        c3 = c3_list(m)
        d.update(c3[1])
    pprint.pprint(d)
    return d


def cc_list(module_name):
    # ex_list = ['ext1', 'ext2', 'ext3']
    l = []
    list_1 = list_con('ext1', module_name)
    list_2 = list_con('ext2', module_name)
    list_3 = list_con('ext3', module_name)
    for e1 in list_1:
        for e2 in list_2:
            for e3 in list_3:
                a = [module_name,e1]
                a.append(e2)
                a.append(e3)
                l.append(a)
    # 模块对应所有 ext1,ext2, ext3的取值
    ll = [module_name, list_1, list_2, list_3]
    return l, ll


def msg_list():
    """得到全部msgtype"""
    db = MySQLdb.connect(**sql_config)
    # 只统计最近一周的 msgtype
    # sql = '''select distinct msgtype from stats where stat_time > '{}' '''.format(week_str)
    # sql = """select msgtype from stats_info where `interval` != 0 and msgtype in
    #     (select distinct(msgtype) from stats where stat_time > '{}')""".format(week_str)
    sql = """select msgtype from stats_info where stat_big_type in ('crawl', 'account')"""
    # sql = '''select distinct msgtype from stats'''
    cur = db.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    db.close()
    m_list = [i[0] for i in data]
    return m_list


def get_msg(msgtype_list):
    try:
        x_msg = ''
        x_string = ''
        msg_p ="<br><br><h2>MySQL统计</h2><br>"
        str_p = "\n\n---{}---\n".format('MySQL')
        x = PrettyTable(["msgtype","ext1","ext2",'ext3',"昨天","今天","近1h","近5min"])
        x.align["msgtype"] = "l"
        x.border = True
        # x.padding_width = 10
        # 返回所有 ext 的可能值，用来 rowspan 表格
        ext_list = []
        x_list = []  # 没有格式化成 pretty table 的 列表集合
        # big_dict = defaultdict(dict)
        big_dict = {}
        for module_name in msgtype_list:
            # ccc = cc_list(module_name)
            # cjol_list = ccc[0]
            # ext_list.append(ccc[1])
            cjol_list = c3_list(module_name)[0]
            for i in cjol_list:
                # print i
                aa = get_mysql(i[0], ext1=i[1], ext2=i[2], ext3=i[3])
                row = [module_name, i[1], i[2], i[3]]
                row.extend(aa)
                bb = {'tl':aa[0], 'tt':aa[1], 't1':aa[2],'t5':aa[3]}
                if module_name not in big_dict:
                    big_dict[module_name]={}
                if i[1] not in big_dict[module_name]:
                    # print i[1]
                    big_dict[module_name][i[1]] = {}
                if i[2] not in big_dict[module_name][i[1]]:
                    # print i[2]
                    big_dict[module_name][i[1]][i[2]] = {}
                    # print i[3]
                if i[3] not in big_dict[module_name][i[1]][i[2]]:
                    big_dict[module_name][i[1]][i[2]][i[3]] = {}
                big_dict[module_name][i[1]][i[2]][i[3]] = bb
                # print module_name
                # print big_dict, '----------------------------'

                # row_dict = {'content':{'module_name':row[0], 'content':{'ext1':row[1], 'content':{'ext2':row[2], 'content':{'ext3':row[3], 'tl':row[4], 'tt':row[5], 't1':row[6],'t5':row[7]}}}}}
                row_dict = {row[0]:{row[1]:{row[2]:{row[3]:{'tl':row[4], 'tt':row[5], 't1':row[6],'t5':row[7]}}}}}

                x_list.append(row_dict)
                x.add_row(row)
            x.sortby = u'msgtype'
            # x_string = str_p + x.get_string(fields=fields_list).encode('utf8')
            # xcontent = x.get_html_string(fields=fields_list)
            x_string = str_p + x.get_string().encode('utf8')
            xcontent = x.get_html_string()
            x_msg = msg_p + xcontent.encode('utf8')

    except Exception, e:
        print Exception, str(e)
    # print x_msg, x_string
    ext_list.sort()
    return x_msg, x_string, ext_list, x_list, big_dict


def list_crr(sql):
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    print sql
    cursor.execute(sql)
    data = cursor.fetchall()
    ll = [i[0] for i in data]
    print ll
    return ll


def c5_list():
    """返回一个有结构的树形字典"""
    all_msgtype_sql = """select msgtype from stats_info where stat_big_type in ('crawl', 'account')"""
    all_msgtype = list_crr(all_msgtype_sql)
    dd = Vividict()
    for m in all_msgtype:
        ext1_sql = """select DISTINCT ext1 from stats where msgtype = '{}' and stat_time > '{}' """.format(m, week_str)
        ll_ext1 = list_crr(ext1_sql)
        for ll1 in ll_ext1:
            ext2_sql = """select distinct(ext2) from stats where msgtype = '{}' and ext1 = '{}'  and stat_time > '{}'""".format(m, ll1, week_str)
            ll_ext2 = list_crr(ext2_sql)
            for ll2 in ll_ext2:
                ext3_sql = """select distinct(ext3) from stats where msgtype = '{}' and ext1 = '{}' and ext3 = '{}'  and stat_time > '{}'""".format(m, ll1, ll2, week_str)
                ll_ext3 = list_crr(ext3_sql)
                for ll3 in ll_ext3:
                    dd[m][ll1][ll2][ll3] = {}
    pprint.pprint(dd)
    return dd


def get_msg2():
    try:
        x_msg = ''
        x_string = ''
        msg_p ="<br><br><h2>MySQL统计(近3天出现的项）</h2><br>"
        str_p = "\n\n---{}---\n".format('MySQL')
        x = PrettyTable(["msgtype","ext1","ext2",'ext3',"昨天","今天","近1h","近5min"])
        x.align["msgtype"] = "l"
        x.border = True
        # x.padding_width = 10
        # 返回所有 ext 的可能值，用来 rowspan 表格
        # big_dict = defaultdict(dict)
        big_dict = c4_list()
        b2_dict = copy.deepcopy(big_dict)
        for i in big_dict:
            for i2 in big_dict[i]:
                for i3 in big_dict[i][i2]:
                    for i4 in big_dict[i][i2][i3]:
                        # print i, i2, i3, i4
                        aa = get_mysql(i, ext1=i2, ext2=i3, ext3=i4)
                        bb = {'tl':aa[0], 'tt':aa[1], 't1':aa[2],'t5':aa[3]}
                        b2_dict[i][i2][i3][i4] = bb
                        row = [i, i2, i3, i4]
                        row.extend(aa)
                        x.add_row(row)
        x.sortby = u'msgtype'
        # print x
        x_string = str_p + x.get_string().encode('utf8')

    except Exception, e:
        print Exception, str(e)
    # print x_msg, x_string
    return x_string,  b2_dict


def html_num(a_dict):
    total_line = 0  # 总行数
    count_0 = len(a_dict) # msgtype个数
    # print count_0
    b_dict = copy.deepcopy(a_dict)
    for i_0 in a_dict:
        total_0 = sum(len(a_dict[i_0][i][i_2]) for i in a_dict[i_0] for i_2 in a_dict[i_0][i])
        b_dict[i_0]['num'] = total_0
        for i_1 in a_dict[i_0]:
            total_1 = sum(len(a_dict[i_0][i_1][i]) for i in a_dict[i_0][i_1])
            b_dict[i_0][i_1]['num'] = total_1
            for i_2 in a_dict[i_0][i_1]:
                total_2 = len(a_dict[i_0][i_1][i_2])
                b_dict[i_0][i_1][i_2]['num'] = total_2

    return b_dict


def html_create():
    # MySQL 里所有可能的值
    aa = get_msg2()
    x_string = aa[0]
    a_dict = aa[1]
    c_dict = copy.deepcopy(a_dict)
    b_dict = html_num(c_dict)
    html = '''<br><br><h2>MySQL统计</h2><br>
        <table><tbody><tr>
        <th>msgtype</th>
        <th>ext1</th>
        <th>ext2</th>
        <th>ext3</th>
        <th>昨天</th>
        <th>今天</th>
        <th>近1h</th>
        <th>近5m</th>
    </tr>'''
    for i_0 in sorted(a_dict.keys()): #msgtype
        # if b_dict[i_0]['num'] > 0:
        html_line = '<tr>'
        html_line += '<td rowspan="{}" >'.format(b_dict[i_0]['num']) + i_0 + '</td>'
            # b_dict[i_0]['num'] = 0
        # count_1 = len(a_dict[i_0])  # ext1个数
        # total_0 = 0  # msgtype 行数
        # total_1 = 0  # ext1 行数
        # total_2 = 0  # ext2 行数
        c1 = 1
        for i_1 in sorted(a_dict[i_0].keys()): # ext1
            if c1 != 1:
                html_line += '<tr>'
            # if b_dict[i_0][i_1]['num'] > 0:
            html_line += '<td rowspan="{}" >'.format(b_dict[i_0][i_1]['num']) + i_1 + '</td>'
            b_dict[i_0][i_1]['num'] = 0
            # else:
            #     html_line += '<tr>'
            # count_2 = len(a_dict[i_0][i_1])  # ext2 个数
            c1 +=1
            c2 = 1
            for i_2 in sorted(a_dict[i_0][i_1].keys()): # ext2
                if c2 != 1:
                    html_line += '<tr>'
                html_line += '<td rowspan="{}" >'.format(b_dict[i_0][i_1][i_2]['num']) + i_2 + '</td>' # + '</tr>'
                b_dict[i_0][i_1][i_2]['num'] = 0
                c2 += 1
                c3 = 1
                for i_3 in a_dict[i_0][i_1][i_2]:
                    if c3 != 1:
                        html_line += '<tr>'
                    html_line += '<td>' + i_3 + '</td>'
                    html_line += '<td>' + str(a_dict[i_0][i_1][i_2][i_3]['tl']) + '</td>'
                    html_line += '<td>' + str(a_dict[i_0][i_1][i_2][i_3]['tt']) + '</td>'
                    html_line += '<td>' + str(a_dict[i_0][i_1][i_2][i_3]['t1']) + '</td>'
                    html_line += '<td>' + str(a_dict[i_0][i_1][i_2][i_3]['t5']) + '</td>' + '</tr>'
                    c3 += 1
        html += html_line

    html += '</tbody></table>'
    # print b_dict
    # print html
    return html, x_string


if __name__ == '__main__':
    # c5_list()
    c4_list()