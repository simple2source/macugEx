# -*- coding:UTF-8 -*-
"""
自动化测试51job,智联,cjol透传代理是否可用
"""
import sys,urllib2,time,json,datetime
import traceback
import random
import InputSearch
import BaseFetch
import smtplib,ConfigParser
from email.mime.text import MIMEText
reload(sys)
sys.setdefaultencoding('utf-8')


class TransferTest(object):
	def __init__(self, job51=None, zhilian=None, cjol=None):
		self.job51 = job51
		self.zhilian = zhilian
		self.cjol = cjol
		self.job51_url = r'http://123.58.128.216:8086/job51/?page=' + str(random.choice(range(1, 10))) + '&area=北京' + \
							'&degree=本科' + '&keyword=java' + '&industry=计算机软件'
		self.zhilian_url = r'http://123.58.128.216:8086/zhilian/?page=' + str(random.choice(range(1, 9))) + '&area=上海' + \
							'&degree=7%2C7' + '&keyword=php' + '&year=3%2C99'
		self.cjol_url = r'http://123.58.128.216:8086/cjol/?page=' + str(random.choice(range(1, 4))) + '&area=深圳' + \
						'&degree=60' + '&keyword=ios'
		self.url_id = r'http://123.58.128.216:8086'
		self.url_worktitle = r'http://123.58.128.216:8086/task/'

	def job51_test(self):
		try:
			msg = []
			result = None
			try:
				t0 = time.time()
				html = urllib2.urlopen(self.job51_url, timeout=15).read()
				t1 = str('%.2f' % (time.time() - t0)) + 's'
				t2 = time.time()
				result = json.loads(html)
				t3 = str('%.2f' % (time.time() - t2)) + 's'
			except Exception, error:
				print traceback.format_exc(), error
				with open('/data/fetch/db/test_http_error.txt', 'w+') as f_error:
					f_error.write(traceback.format_exc())
				sys.exit()

			update_vistat = InputSearch.TransportSearch()
			update_vistat.get_post_viewstat()
			if result:
				msg.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
				msg.append(result['page_count'])
				msg.append(result['resume_count'])
				msg.append(str(len(result['resume_list'])))
				msg.append(t1)
				msg.append(t3)
				resume_id = random.choice(result['resume_list'])['id']
				url_id = self.url_id + '/id51/?id=' + resume_id
				t4 = time.time()
				resume = urllib2.urlopen(url_id).read()
				t5 = str('%.2f' % (time.time() - t4)) + 's'
				result_id = json.loads(resume)['msg']
				msg.append(result_id)
				msg.append(t5)
				msg.append(self.job51_url.replace('&', '&amp'))
				msg.append(str(resume_id))
			print msg, '++++++'
			time.sleep(3)
			return msg

		except Exception, e:
			print e, traceback.format_exc()
			msg = None
			return msg

	def worktitle_test(self):
		try:
			result = urllib2.urlopen(self.url_worktitle, timeout=15).read()
			result = '<h1><a href="http://123.58.128.216:8086/task/">接口访问</a></h1>' +\
					result.replace('<table>', '<table class="table">').replace('<th>', "<th class='table'>")
			return result
		except Exception, error:
			msg = error
			return msg

	def auto_test_email(self, title='', msg_txt=''):
		try:
			cf = ConfigParser.ConfigParser()
			cf.read('/data/fetch/conf/basic.conf')
			host = cf.get('email', 'server')
			user_name = cf.get('email', 'username')
			user_passwd = cf.get('email', 'password')
			default_user = cf.get('email', 'default_users')
			default_list = []
			for m in default_user.split(';'):
				if m and default_list.count(m) == 0:
					default_list.append(m)
			users = default_list

			if host and user_name and user_passwd and users:
				msg = MIMEText(msg_txt, _subtype='html', _charset='UTF-8')
				msg['Subject'] = title
				msg['From'] = user_name
				msg['To'] = ';'.join(users)
				s = smtplib.SMTP()
				s.connect(host)
				s.login(user_name, user_passwd)
				s.sendmail(user_name, users, msg.as_string())
				s.close()
				return True
			else:
				return False
		except Exception, e:
			print e, traceback.format_exc()
			msg = None
			return msg

	def zhilian_test(self):
		try:
			msg = []
			result = None
			try:
				t0 = time.time()
				html = urllib2.urlopen(self.zhilian_url, timeout=15).read()
				t1 = str('%.2f' % (time.time() - t0)) + 's'
				t2 = time.time()
				result = json.loads(html)
				t3 = str('%.2f' % (time.time() - t2)) + 's'
			except Exception, error:
				print 'Error:-----', error
				sys.exit()
			if result:
				msg.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
				msg.append(result['page_count'])
				msg.append(result['resume_count'])
				msg.append(str(len(result['resume_list'])))
				msg.append(t1)
				msg.append(t3)
				resume_id = random.choice(result['resume_list'])['id']
				url_id = self.url_id + '/idz/?id=' + resume_id
				t4 = time.time()
				resume = urllib2.urlopen(url_id).read()
				t5 = str('%.2f' % (time.time() - t4)) + 's'
				result_id = json.loads(resume)['msg']
				msg.append(result_id)
				msg.append(t5)
				msg.append(self.zhilian_url.replace('&', '&amp'))
				msg.append(resume_id)
			print msg, '+++++++++'
			time.sleep(3)
			return msg

		except urllib2.URLError, e:
			print e, traceback.format_exc()
			msg = None
			return msg

	def cjol_test(self):
		try:
			msg = []
			result = None
			try:
				t0 = time.time()
				html = urllib2.urlopen(self.cjol_url, timeout=15).read()
				t1 = str('%.2f' % (time.time() - t0)) + 's'
				t2 = time.time()
				result = json.loads(html)
				t3 = str('%.2f' % (time.time() - t2)) + 's'
			except Exception, error:
				print 'Error:+++++++', error
			if result:
				msg.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
				msg.append(result['page_count'])
				msg.append(result['resume_count'])
				msg.append(str(len(result['resume_list'])))
				msg.append(t1)
				msg.append(t3)
				resume_id = random.choice(result['resume_list'])['id']
				url_id = self.url_id + '/idc/?id=' + resume_id
				t4 = time.time()
				resume = urllib2.urlopen(url_id).read()
				t5 = str('%.2f' % (time.time() - t4)) + 's'
				result_id = json.loads(resume)['msg']
				msg.append(result_id)
				msg.append(t5)
				msg.append(self.cjol_url.replace('&', '&amp'))
				msg.append(resume_id)
			print msg, '+++++++++'
			return msg

		except (urllib2.HTTPError, urllib2.URLError), e:
			print e, traceback.format_exc()
			msg = None
			return msg


	def result_mail(self):
		try:
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
<h2>透传自动化测试表</h2>
<table>

    <tr>
        <th>抓取来源</th>
        <th>测试时间</th>
        <th>页面数统计</th>
        <th>简历数统计</th>
        <th>当前页面简历数</th>
        <th>抓取耗时</th>
        <th>json加载耗时</th>
        <th>id入库状态</th>
        <th>入库耗时</th>
        <th>测试链接</th>
        <th>测试简历id</th>
    </tr>'''


			if self.job51:
				msg_51 = self.job51_test()
				if msg_51:
					label_0 = '<tr>' + '<td>51job</td>'
					for label in msg_51:
						label_0 += '<td>' + str(label) + '</td>'
					job51_table = label_0 + '</tr>'
				else:
					job51_table = '<tr>' + '<td>51job</td>' + '<td>' + \
					              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '</td>' +'<td class="bg-error">' * 7 + \
					              '</td>' +'<td>'+ self.job51_url.replace('&', '&amp') + '</td>'+ '<td class="bg-error"> </td>' + '</tr>'
			else:
				job51_table = '<tr>' + '<td>51job</td>' + '<td>' + \
				              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '</td>' + '<td>  </td>' * 7 + \
				              '<td>' + self.job51_url.replace('&', '&amp') + '</td>' + '<td class="bg-error"> </td>' + '</tr>'


			if self.zhilian:
				msg_zhilian = self.zhilian_test()
				if msg_zhilian:
					label_1 = '<tr>' + '<td>智联</td>'
					for label in msg_zhilian:
						label_1 += '<td>' + str(label) + '</td>'
					zhilian_table = label_1 + '</tr>'
				else:
					zhilian_table = '<tr>' + '<td>智联</td>' + '<td>' + \
					                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '</td>' +'<td class="bg-error">' * 7 + \
					                '</td>' + '<td>' + self.zhilian_url.replace('&', '&amp') + '</td>' + '<td class="bg-error"> </td>' + '</tr>'
			else:
				zhilian_table = '<tr>' + '<td>智联</td>' + '<td>' + \
				                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '</td>' + '<td>  </td>' * 7 + \
				                '<td>' + self.zhilian_url.replace('&', '&amp') + '</td>' + '<td class="bg-error"> </td>' + '</tr>'


			if self.cjol:
				msg_cjol = self.cjol_test()
				if msg_cjol:
					label_2 = '<tr>' + '<td>cjol</td>'
					for label in msg_cjol:
						label_2 += '<td>' + str(label) + '</td>'
					cjol_table = label_2 + '</tr>'
				else:
					cjol_table = '<tr>' + '<td>cjol</td>' + '<td>' + \
					             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '</td>' + '<td class="bg-error">' * 6 + \
					             '</td>' + '<td>' + self.cjol_url.replace('&', '&amp') + '</td>' + '<td class="bg-error"> </td>' + '</tr>'
			else:
				cjol_table = '<tr>' + '<td>cjol</td>' + '<td>' + \
				             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '</td>' + '<td>  </td>' * 6 + \
				             '<td>' + self.cjol_url.replace('&', '&amp') + '</td>' + '<td class="bg-error"> </td>' + '</tr>'

			msg = msg_style + job51_table + zhilian_table + cjol_table + '</table>' + '</br>' + \
				'注:json加载时间仅用自动化测试时统计，实际请求无需考虑' +'</body>' + '</html>'
			msg = msg.replace('<table>', '<table class="table">').replace('<th>', "<th class='table'>")
			return msg

		except Exception, e:
			print e, traceback.format_exc()
			sys.exit()


if __name__ == '__main__':
	app = TransferTest(job51='job51', zhilian='zhilian', cjol='cjol')
	arguments = sys.argv[1]
	if arguments == 'test':
		msg = app.result_mail()
		print msg
	elif arguments == 'tmail':
		msg = app.result_mail()
		send_msg = BaseFetch.BaseFetch()
		send_msg.send_mails('报表07:透传自动化测试状态', msg, 0)
	elif arguments == 'test1':
		msg = app.worktitle_test()
		print msg
	elif arguments == 'wmail':
		msg = app.worktitle_test()
		app.auto_test_email('报表8：worktitle接口测试', msg)
