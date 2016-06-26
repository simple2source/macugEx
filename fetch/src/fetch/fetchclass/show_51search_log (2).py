# -*- coding:UTF-8 -*-

import os,sqlite3,datetime,time
from common import *
import disk2
from prettytable import PrettyTable
import sys,datetime
reload(sys)
sys.setdefaultencoding('utf-8')
from show_mysql import *
import BaseFetch
import traceback

def query_search():
	'''抽取sqlite3不同年龄段进度
	   运行状态'''
	try:
		conn = sqlite3.connect('/data/fetch/database/search_log.db')
		today_str = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
		cur = conn.cursor()
		age_list = [[20, 21], [22], [23], [24], [25], [26], [27], [28], [29], [30], [31], [32], [33], [34, 35],
					[36, 37], [38, 39], [40, 41, 42],[43, 44], [46, 47, 48, 49, 50]]
		age_result = []

		for i in age_list:
			and_str = ''
			and_list = []
			query_result = []
			for j in i:
				and_list.append("age = %d" % j)
			and_str = (" or ").join(and_list)
			query_sql = 'select age,current_circle,start_time,total_resume,total_insert,total_update,condition_count from search_log where %s order by id desc limit 1' % and_str
			query_sql_today = 'select sum(seg_count) from search_log where at_time > "%s" and (%s)' % (today_str, and_str)
			query_sum = cur.execute(query_sql_today).fetchall()[0][0]
			print query_sql
			query_result = list(cur.execute(query_sql).fetchall()[0])
			total_count = 1
			while total_count <= 3:
				last_current = query_result[1] - total_count
				query_time = 'select start_time,at_time from search_log where current_circle= %s and (%s) order by id desc limit 1' % (last_current,and_str)
				last_time = cur.execute(query_time)
				last_time = last_time.fetchall()[0]
				last_time_start = last_time[0]
				last_time_end = last_time[1]
				waste_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(last_time_end, "%Y-%m-%d %H:%M:%S"))) - datetime.datetime.fromtimestamp(time.mktime(time.strptime(last_time_start, "%Y-%m-%d %H:%M:%S")))
				waste_time = '%.2f' % (waste_time.seconds / 3600.0)
				query_grab = 'select sum(seg_count) from search_log where current_circle=%s and (%s)' % (last_current,and_str)
				seg_grab = cur.execute(query_grab).fetchall()[0][0]
				last_grab_time = str(seg_grab) + '/' + str(waste_time) + 'h'
				query_result.append(last_grab_time)
				total_count += 1
			query_result.append(query_sum)
			age_result.append(query_result)
		conn.close()
		return age_result

	except Exception, e:
		print traceback.format_exc()
		print e

def query_progress():
	'''抽取sqlite3不同年龄段
	   当前运行状态'''
	try:
		conn = sqlite3.connect('/data/fetch/database/search_log.db')
		cur = conn.cursor()
		age_list = [[20, 21], [22], [23], [24], [25], [26], [27], [28], [29], [30], [31], [32], [33], [34, 35],
					[36, 37], [38, 39], [40, 41, 42], [43, 44], [46, 47, 48, 49, 50]]
		age_result = []

		for i in age_list:
			add_list = []
			for j in i:
				add_list.append("age = %d" % j)
			and_str =(' or ').join(add_list)
			query_sql = 'select age, at_time,deg,area,year,gen,seg_count,resume_insert,resume_update,resume_sum,current_page,exatly_page,sum_page from search_log where %s order by id desc limit 1' % and_str
			print query_sql
			query_circle = 'select current_circle from search_log where %s order by id desc limit 1' % and_str
			current_circle = cur.execute(query_circle).fetchall()[0][0]
			query_result = list(cur.execute(query_sql).fetchall()[0])
			total_count = 1
			while total_count <= 3:
				last_current = current_circle - total_count
				query_error = 'select page_error_count from search_log where current_circle=%s and (%s) order by id desc limit 1' % (last_current,and_str)
				error_count = cur.execute(query_error).fetchall()[0][0]
				query_result.append(error_count)
				total_count += 1
			age_result.append(query_result)

		conn.close()
		return age_result

	except Exception, e:
		print traceback.format_exc()
		print e

def result_print():
	try:
		search_result = query_search()
		progress_result = query_progress()
		if search_result:
			print search_result
		if progress_result:
			print progress_result
	except Exception, e:
		print e


def result_email():
	'''sqlite3查询结果
	   格式化html'''
	try:
		msg_style= '''<html>
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
<h2>抓取进度表</h2>
<table>

    <tr>
        <th class="bg-ok color-ok">年龄</th>
        <th>当前轮次</th>
        <th>开始时间</th>
        <th>总抓取数</th>
        <th>总插入库数</th>
        <th>总更新入库数</th>
        <th>已抓取条件数</th>
        <th>上1轮抓取数/时间</th>
        <th>上2轮抓取数/时间</th>
        <th>上3轮抓取数/时间</th>
        <th>当天总抓取数</th>
        <th>总条件数</th>
    </tr>'''
		progress_table = '''<h1>抓取状态表</h1>
<table>

    <tr>
        <th class="bg-ok color-ok">年龄</th>
        <th>当前抓取时间</th>
        <th>学历</th>
        <th>地区</th>
        <th>工作年限</th>
        <th>性别</th>
        <th>当前抓取个数</th>
        <th>当前插入个数</th>
        <th>当前更新个数</th>
        <th>当前条件简历总数</th>
        <th>当前抓取页面</th>
        <th>搜索显示实际页面</th>
        <th>总页面数</th>
        <th>上1轮异常页面数</th>
        <th>上2轮异常页面数</th>
        <th>上3轮异常页面数</th>
    </tr>'''

		result_1 = query_search()
		condition_count = ['256', '128', '128', '128', '192', '192', '192', '192', '224', '224', '160', '96', '96', '128', '128', '128', '96', '64', '192']
		item_1 = ''
		item_2 = ''
		seg = 0
		for item in result_1:
			for x in item:
				item_1 = item_1 + '<td>' + str(x) + '</td>'
			item_2 = item_2 + '<tr>' + item_1 + '<td>' + condition_count[seg] + '</td>'+ '</tr>'
			seg += 1
			item_1 = ''
		msg_1 = msg_style + item_2 + '</table>'

		result_2 = query_progress()
		item_3 = ''
		item_4 = ''
		for progress_1 in result_2:
			for v in progress_1:
				item_3 = item_3 + '<td>' + str(v) + '</td>'
				if isinstance(v, int) and v >= 2500:
					item_3 = item_3.replace('<td>' + str(v), '<td class="bg-error">' + str(v))
				if isinstance(v, int) and 2500 > v >= 1000:
					item_3 = item_3.replace('<td>' + str(v), '<td class="bg-warning">' + str(v))
			item_4 = item_4 + '<tr>' + item_3 + '</tr>'
			item_3 = ''
		msg_2 = progress_table + item_4 + '</table>' + '</body>' + '</html>'

		msg = msg_1 + '注:代表当前任务对应的年龄段抓取进度' + '<br>'+ msg_2 + '注:代表当前任务对应的年龄段抓取状态' + '<br>' + \
			  '注:红色标识代表当前请求异常' + '<br>' + '注:黄色标识代表简历数在1000-2500'+ '<br>'+ '注:当前简历总数代表当前抓取条件下最近七天简历总数' + '<br>' + \
		'注:异常页面数代表请求到简历总数为3000的不正常页面统计'

		msg = msg.replace('<table>', '<table class="table">').replace('<th>', "<th class='table'>")
		return msg
	except Exception, e:
		print e
		print traceback.format_exc()



if __name__ == '__main__':
	msg = result_email()
	arguments = sys.argv[1]
	if arguments == 'email':
		if msg:
			sendEmail('default_main','报表5：51search抓取进度状态',msg,msg_type=1, des= 'op')
	elif arguments == 'tmail':
		send_msg = BaseFetch.BaseFetch()
		send_msg.send_mails('报表5：51search抓取进度状态',msg,0)
	elif arguments == 'test':
		print msg





