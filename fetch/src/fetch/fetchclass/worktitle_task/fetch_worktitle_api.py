# -*- coding:utf-8 -*-

import urllib2, json, traceback, sys, pickle, datetime, re, copy,os,urllib
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)
import transfer_auto_test

reload(sys)
sys.setdefaultencoding('utf-8')


class WorkTitle(object):
	def __init__(self):
		self.url_week = "https://api.worktile.com/v1/tasks?" \
						"access_token=Vgd_irB7SrI0YUtd5ACG-zrUpqo=4BQrajGW87c2017dfeb741b0f4ef4f851713ac18817609fbc68" \
						"fdf56713d1093be812a3b3deda655304799d758afb6a71cac40d23e2813b83c3ebb7051fcb69850ec5ee3b8b6216" \
						"c37d46d6fe72b625fd4de28cc6cb2afe1a56352932cf226f01fb8b384264c028147a1cc9cf1e7695d50c949bd&" \
						"pid=976b002bbffe4c6ca55a2845b50fbebe&type=all"
		self.url_dig = "https://api.worktile.com/v1/tasks?" \
						"access_token=Vgd_irB7SrI0YUtd5ACG-zrUpqo=4BQrajGW87c2017dfeb741b0f4ef4f851713ac18817609fbc68" \
						"fdf56713d1093be812a3b3deda655304799d758afb6a71cac40d23e2813b83c3ebb7051fcb69850ec5ee3b8b6216" \
						"c37d46d6fe72b625fd4de28cc6cb2afe1a56352932cf226f01fb8b384264c028147a1cc9cf1e7695d50c949bd&" \
						"pid=15ba2b085b2749368bbdb0faf6e9c0db&type=all"
		self.url_week_t = 'https://worktile.com/project/976b002bbffe4c6ca55a2845b50fbebe/task/'
		self.url_dig_t = 'https://worktile.com/project/15ba2b085b2749368bbdb0faf6e9c0db/task/'
		self.update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.complete_dict = {'0': '未完成', '1': '完成', 'None': 'None'}
		self.local_task_new = ''
		self.access_token = '&access_token=Vgd_irB7SrI0YUtd5ACG-zrU' \
		                    'pqo=4BQrajGW87c2017dfeb741b0f4ef4f851713ac188' \
		                    '17609fbc68fdf56713d1093be812a3b3deda655304799d758a' \
		                    'fb6a71cac40d23e2813b83c3ebb7051fcb69850ec5ee3b8b6216c37d' \
		                    '46d6fe72b625fd4de28cc6cb2afe1a56352932cf226f01fb8b384264c028147a1cc9cf1e7695d50c949bd'
		self.users = {
			'planning': {'task': [],
						'group': 'plan',
						'nickname': 'plan'},
			'lyaohe': {
				'group': 'php',
				'nickname': 'liangyaohe',
				'task': []
			},
			'hick': {
				'group': 'php',
				'nickname': 'hick',
				'task': []
			},
			'dengjiaming': {
				'group': 'php',
				'nickname': 'DJM',
				'task': []
			},
			'linkaibin': {
				'group': 'php',
				'nickname': 'lkb',
				'task': []
			},
			'kai893495453': {
				'group': 'php',
				'nickname': 'holy',
				'task': []
			},
			'vk2015': {
				'group': 'app',
				'nickname': 'vk',
				'task': []
			},
			'ZubinXiong': {
				'group': 'app',
				'nickname': 'zubin',
				'task': []
			},
			'rockyhu': {
				'group': 'app',
				'nickname': 'rocky',
				'task': []
			},
			'Sampang': {
				'group': 'python',
				'nickname': 'sam',
				'task': []
			},
			'alvin_liang': {
				'group': 'python',
				'nickname': 'alvin',
				'task': []
			},
			'xander_li': {
				'group': 'python',
				'nickname': 'xander',
				'task': []
			},
			'stormkang': {
				'group': 'python',
				'nickname': 'storm',
				'task': []
			},
			'dkzzeng': {
				'group': 'web',
				'nickname': 'dkzzeng',
				'task': []
			},
			'huahua_lanh': {
				'group': 'php',
				'nickname': 'jeff',
				'task': []
			},
			'tekyli': {
				'group': 'python',
				'nickname': 'teky',
				'task': []
			},
			'echo_hupei': {
				'group': 'web',
				'nickname': 'echo',
				'task': []
			},
			'smilyming': {
				'group': 'web',
				'nickname': 'jam',
				'task': []
			}
		}

		self.form_style = '''<html>
<head>
    <meta charset="utf-8">
    <base target="_blank">
</head>
<style type="text/css">
a:link {
color:#2196F3;
text-decoration:none; }
a:visited {
color:#2196F3;
text-decoration:none; }
a:hover {
color:#000000;
text-decoration:none; }
a:active {
color:#2196F3;
text-decoration:none; }
.body{
  font-family: Monaco, Menlo, Consolas, "Courier New", "Lucida Sans Unicode", "Lucida Sans", "Lucida Console",  monospace;
  font-size: 14px;
  line-height: 20px;
}

.table{ border-collapse:collapse; border:solid 1px gray; width=100%}
.table td{border:solid 1px gray; padding:6px; }

.color-ok {color: green;}
.color-warning {color: coral;}
.color-error {color: red;}

.bg-ok {background-color: lavender;}
.bg-warning {background-color: yellow;}
.bg-error {background-color: deeppink;}
</style>

<body class="body">
<table class="table">
'''

	def fetch_api_data(self, flag=0):
		try:
			data = None
			if flag == 0:
				try:
					data = json.loads(urllib2.urlopen(self.url_week).read())
					data.pop(0)                                                 # worktitle接口返回了第一条错误记录，暂时先去掉
					f_pickle = open('/data/fetch/db/week_api.plk', 'wb')
					pickle.dump(data, f_pickle)
					f_pickle.close()
					with open('/data/fetch/db/cache_time', 'wb') as f_cache_time:
						f_cache_time.write(self.update_time)

				except urllib2.HTTPError, error:
					f_pickle = open('/data/fetch/db/week_api.plk', 'rb')
					data = pickle.load(f_pickle)
					f_pickle.close()
					with open('/data/fetch/db/cache_time', 'rb') as f_cache_time:
						self.update_time = f_cache_time.read()
					print error.read()

			elif flag == 1:
				try:
					data = json.loads(urllib2.urlopen(self.url_dig).read())
					f_pickle = open('/data/fetch/db/dig_api.plk', 'wb')
					pickle.dump(data, f_pickle)
					f_pickle.close()

				except urllib2.HTTPError, error:
					f_pickle = open('/data/fetch/db/dig_api.plk', 'rb')
					data = pickle.load(f_pickle)
					f_pickle.close()
					print error.read()
			return data

		except Exception, e:
			print e

	def user_data(self):
		try:
			data = {'php': [], 'python': [], 'web': [], 'app': [], 'planning': []}
			fetch_week = self.fetch_api_data()
			fetch_week_count = len(fetch_week)
			seg = 0
			fetch_dig = self.fetch_api_data(flag=1)
			fetch_data = fetch_week + fetch_dig
			for x in fetch_data:
				task_dict = {'title': '', 'url': '', 'completed': '', 'entry_name': '', 'created_at': '',
							'completed_date': '', 'desc': ''}
				seg += 1
				if x['members']:
					for y in x['members']:
						if y['name'] not in self.users.keys():
							continue
						match_obj = re.match(r'[0-9].', x['name'])
						if not match_obj:
							x['name'] = '5.' + x['name']
							try:
								opener = urllib2.build_opener(urllib2.HTTPHandler)
								put_url = 'https://api.worktile.com/v1/tasks/' + x['tid'] + '?' + 'pid=' + x['pid'] + self.access_token
								put_dict = {}
								put_dict['name'] = x['name']
								put_dict['desc'] = x['desc']
								put_data = urllib.urlencode(put_dict)
								request = urllib2.Request(put_url, data=put_data)
								request.get_method = lambda: 'PUT'
								result = opener.open(request)
								if int(result.getcode()) == 200:
									email_changed_title = transfer_auto_test.TransferTest()
									email_title = x['name'] + '-标题优先级修改成功'
									url_title = self.url_week_t + x['tid']
									msg_text = '<B>' + '<a href={}>'.format(url_title) + email_title + '</a>' + '</B>' +\
												'</br>' + '内容:' + '</br>' + x['desc']
									email_changed_title.auto_test_email(email_title, msg_text)
									print 'update success !!!!!'
							except Exception, e:
								print e, traceback.format_exc(), x['name']

						task_dict['title'] = x['name']
						if seg <= fetch_week_count:
							task_dict['url'] = self.url_week_t + x['tid']
						else:
							task_dict['url'] = self.url_dig_t + x['tid']
						task_dict['completed'] = x['completed']
						task_dict['entry_name'] = x['entry_name']
						task_dict['created_at'] = x['created_at']
						task_dict['completed_date'] = x['completed_date']
						task_dict['desc'] = x['desc']
						self.users[y['name']]['task'].append(task_dict)
				else:
					match_obj = re.match(r'[0-9].', x['name'])
					if not match_obj:
						x['name'] = '5.' + x['name']
						# try:                         # 暂时没有分配成员的任务
						# 	opener = urllib2.build_opener(urllib2.HTTPHandler)
						# 	put_url = 'https://api.worktile.com/v1/tasks/' + x['tid'] + '?' + 'pid=' + x['pid'] + self.access_token
						# 	put_data = 'name=' + x['name'] + '&' + 'desc=' + x['desc']
						# 	request = urllib2.Request(put_url, data=put_data)
						# 	request.get_method = lambda: 'PUT'
						# 	result = opener.open(request)
						# 	if int(result.getcode()) == 200:
						# 		print 'update success !!!!!'
						# except Exception, e:
						# 	print traceback.format_exc(), e, x['name']

					task_dict['title'] = x['name']
					if seg <= fetch_week_count:
						task_dict['url'] = self.url_week_t + x['tid']
					else:
						task_dict['url'] = self.url_dig_t + x['tid']
					task_dict['created_at'] = x['created_at']
					task_dict['entry_name'] = x['entry_name']
					task_dict['desc'] = x['desc']
					self.users['planning']['task'].append(task_dict)

			for user in self.users:
				if self.users[user]['group'] == 'php':
					data['php'].append(self.users[user])

				elif self.users[user]['group'] == 'python':
					data['python'].append(self.users[user])

				elif self.users[user]['group'] == 'web':
					data['web'].append(self.users[user])

				elif self.users[user]['group'] == 'app':
					data['app'].append(self.users[user])

				elif self.users[user]['group'] == 'plan':
					data['planning'].append(self.users[user])

			print '------>'
			return data

		except Exception, e:
			print e, traceback.format_exc()

	def form_data(self, flag=0):
		try:
			data = self.user_data()
			if flag == 0:
				msg = {'update_time': '', 'groups': ''}
				msg['update_time'] = self.update_time
				msg['groups'] = data
				return msg

			elif flag == 1:
				msg = ''
				f_last_local_comp = open('/data/fetch/db/task_completed.plk', 'r')
				task_last_local_comp = pickle.load(f_last_local_comp)          # 上次从本地读取的记录，用来与本次对比新增的记录
				f_last_local_uncomp = open('/data/fetch/db/task_uncompleted.plk', 'r')
				task_last_local_uncomp = pickle.load(f_last_local_uncomp)
				f_last_local_new = open('/data/fetch/db/task_new_list.plk', 'rb')
				person_new_list = pickle.load(f_last_local_new)                # 上次新增的记录读取，用来增加新增任务并保存到本地
				task_completed = []                                            # 本次完成的记录用来保存到本地覆盖上次的
				task_uncompleted = []
				self.local_task_new = copy.deepcopy(person_new_list)
				for group in data:
					group_common = ''
					msg_group = '<td style="width:360px;vertical-align:top">' + \
															'<h3>' + group + '</h3>'
					person_recent_dict = {}
					for person in data[group]:
						msg_name = '<B>' + person['nickname'] + '</B>' + '<br>'
						msg_task = ''
						person_task = sorted(person['task'], key=lambda x: x['title'][0], reverse=True)
						person_task = sorted(person_task, key=lambda x: x['completed'])
						if not person_task:
							group_common = group_common + msg_name + '<div style=" max-width:336px;display:block;white-space:nowrap;' \
							                          ' overflow:hidden; text-overflow:ellipsis;"' + '<a>' + \
							               '暂无任务' + '</a>' + '</div>' + '</br>'
							continue
						task_recent_list = []
						person_recent_dict['nickname'] = person['nickname']
						person_recent_dict['group'] = group
						for task in person_task:
							task_recent_dict = {}
							if task['completed'] == 1:
								task_title = '<s>' + '<font color="gray">' + task['title'] + '</font>' + '</s>'
								task_completed.append(task['url'])
								if task['url'] not in task_last_local_comp:
											# 判断本次任务是否在上次本地记录的任务当中，如果不存在，则标记为新增的任务
									task_recent_dict['title'] = task['title']
									task_recent_dict['url'] = task['url']
									task_recent_dict['entry_name'] = task['entry_name']
									task_recent_dict['completed'] = 1
									interrupt = False
									for count_1, person_new in enumerate(person_new_list):
										if interrupt:                               # 迭代保存的新增任务，避免已存在的新增的和已完成的重复添加
											break
										for count_2, check in enumerate(person_new['task']):
											if check['url'] == task['url']:
												self.local_task_new[count_1]['task'][count_2]['completed'] = 1
												task_recent_dict = {}
												interrupt = True
												break

							else:
								task_title = task['title']
								task_uncompleted.append(task['url'])
								if task['url'] not in task_last_local_uncomp:
									task_recent_dict['title'] = task['title']
									task_recent_dict['url'] = task['url']
									task_recent_dict['entry_name'] = task['entry_name']
									task_recent_dict['completed'] = 0
								if int(task_title[0]) > 5:
									task_title = '<font color=#FF9800>' + task_title + '</font>'

							msg_task = msg_task + '<div style=" max-width:336px;display:block;white-space:nowrap; ' \
							                      'overflow:hidden; text-overflow:ellipsis;"' +'<a>' + \
							           '[' + task['entry_name'] + ']' + '</a>' + '<a>' + \
							           '<a href={}>'.format(task['url']) + task_title + '</a>' + '</div>'
							if task_recent_dict:
								task_recent_list.append(task_recent_dict)
							group_one = msg_name + msg_task
						if task_recent_list:
							print 'xxxxxxxx'
							person_recent_dict['task'] = task_recent_list[:]
							person_data = copy.deepcopy(person_recent_dict)        # 使用深copy，避免变量在内存中指向同一个位置
							nickname_list = []
							for x, y in enumerate(person_new_list):
								nickname_list.append(y['nickname'])
								if y['nickname'] == person_data['nickname']:
									new_task = self.local_task_new[x]['task'] + person_data['task']
									self.local_task_new[x]['task'] = new_task

							else:
								if not person_new_list:
									self.local_task_new.append(person_data)
								else:
									if person_data['nickname'] not in nickname_list:
										self.local_task_new.append(person_data)

						group_common = group_common + group_one + '</br>'
					msg = msg + msg_group + group_common + '</td>'

				msg = self.form_style + msg + '</tr>' + '</table>' + '</body></html>'

				with open('/data/fetch/db/task_completed.plk', 'w+') as f_completed:  # 已完成的任务加入到列表中保存到本地
					pickle.dump(task_completed, f_completed)
					f_completed.close()

				with open('/data/fetch/db/task_uncompleted.plk', 'w+') as f_uncompleted:
					pickle.dump(task_uncompleted, f_uncompleted)
					f_uncompleted.close()
				person_new_list = []
				with open('/data/fetch/db/task_new_list.plk', 'wb') as f_new_list:      # 当天新增的任务记录到本地
					pickle.dump(self.local_task_new, f_new_list)
					f_new_list.close()
			print self.local_task_new
			return msg
		except Exception, e:
			print e, traceback.format_exc()

	def email_task_status(self, flag=0):
		data = {'php': [], 'python': [], 'web': [], 'app': [], 'planning': []}
		msg = ''
		if self.local_task_new:
			for person_dict in self.local_task_new:
				data[person_dict['group']].append(person_dict)

			for group in data:
				group_common = ''
				msg_group = '<td style="width:360px;vertical-align:top">' + \
														'<h3>' + group + '</h3>'
				if not data[group]:
					continue
				for person in data[group]:
					msg_name = '<B>' + person['nickname'] + '</B>' + '<br>'
					msg_task = ''
					person_task = sorted(person['task'], key=lambda x: x['title'][0], reverse=True)
					person_task = sorted(person_task, key=lambda x: x['completed'])
					for task in person_task:
						if task['completed'] == 1:
							task_title = '<s>' + '<font color="gray">' + task['title'] + '</font>' + '</s>'
						else:
							task_title = task['title']
							if int(task_title[0]) > 5:
								task_title = '<font color=#FF9800>' + task_title + '</font>'
						print task['url'], '000000'
						msg_task = msg_task + '<div style=" max-width:336px;display:block;white-space:nowrap; ' + \
						           'overflow:hidden; text-overflow:ellipsis;"' +'<a>' + '[' + task['entry_name'] + ']' + \
						           '</a>' + '<a>' + '<a href={}>'.format(task['url']) + task_title + '</a>' + '</div>'

						group_one = msg_name + msg_task
					group_common = group_common + group_one + '</br>'
				msg = msg + msg_group + group_common + '</td>'

			msg = self.form_style.replace('<body class="body">', '<body class="body"><h1><B>当天任务进度:</B></h1>') +\
			      msg + '</tr>' + '</table>' + '</body></html>'
		if not msg:
			msg = self.form_style.replace('<body class="body">', '<body class="body"><h1><B>当天任务进度:</B></h1>') +\
			      '<font color=#7E3D76>当前任务进度没有更新</font>'  + '</table>' + '</body></html>'
		if flag == 1:
			empty_list = []
			with open('/data/fetch/db/task_new_list.plk', 'wb') as f_new_list:
				pickle.dump(empty_list, f_new_list)
				f_new_list.close()
				#  每天邮件报表将当天新增的任务或者完成的任务清除掉
		return msg


if __name__ == '__main__':
	app = WorkTitle()
	app.form_data(flag=1)
	em = transfer_auto_test.TransferTest()
	if len(sys.argv) > 1:
		if sys.argv[1] == 'e0':
			msg = app.email_task_status(flag=0)
			em.auto_test_email('报表09：worktitle任务进度', msg)
		elif sys.argv[1] == 'e1':
			msg = app.email_task_status(flag=1)
			em.auto_test_email('报表09:worktitle任务进度', msg)
		elif sys.argv[1] == 'test':
			msg = app.email_task_status(flag=0)
