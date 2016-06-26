# -*- coding:utf-8 -*-
"""
监控抓取的搜索文件变化，将html中id对应的简历信息，存入到redis
"""

import redis
import urllib
from redispipe import Rdsreport
from bs4 import BeautifulSoup
import logging, time, os, sys
import logging.config
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY


log_file = '/data/fetch_git/fetch/src/fetch/log/update_id2redis.log'
fmt = '%(asctime)s %(filename)s %(funcName)s %(levelname)s Line:%(lineno)s :%(message)s'
# logging.basicConfig(level=logging.DEBUG, filename=log_file, format=fmt, disable_existing_loggerss=False)
loggers = logging.getLogger(__name__)
loggers.level = logging.DEBUG
handlers = logging.FileHandler(log_file)
formatter = logging.Formatter(fmt)
handlers.formatter = formatter
stdout_handler = logging.StreamHandler(sys.__stdout__)
stdout_handler.level = logging.DEBUG
stdout_handler.formatter = formatter
loggers.addHandler(handlers)
loggers.addHandler(stdout_handler)


class SearchIdInfoUpdate(Rdsreport):
	"""将通过搜索抓取到的简历页面的id加密信息更新到redis，
	用来入库时候直接从redis获取加密串信息"""
	def __init__(self):
		Rdsreport.__init__(self)
		self.mark_51 = 'job51_'
		self.mark_zhilian = 'zhilian_'

	def update_job51(self):
		"""51job加密信息更新到redis,设置key生存时间为12h"""
		try:
			t0 = time.time()
			with open('/data/fetch/db/trans/search.html', 'r') as f_read:
				html = f_read.read()
			t1 = time.time() - t0
			loggers.info('load local html use time %s' % str(t1))
			if html.find('trBaseInfo') > 0:
				soup = BeautifulSoup(html, 'html.parser')
				url_list = soup.select('.SearchR a')
				count_update = 0
				for i in url_list:
					id_info = i['href']
					resume_id_key = self.mark_51 + id_info.split('&')[0].split('=')[1]
					if not self.r.get(resume_id_key):
						self.r.set(resume_id_key, id_info, ex=43200)
						count_update += 1
				post_dynamic = soup.select('#__VIEWSTATE')[0]['value']
				post_dynamic = urllib.quote_plus(post_dynamic)
				hidCheckUserIds = soup.select('#hidCheckUserIds')[0]['value']
				hidCheckKey = soup.select('#hidCheckKey')[0]['value']
				hidCheckKey = urllib.quote_plus(hidCheckKey)
				hidValue = soup.select('#hidValue')[0]['value']
				with open('/data/fetch/task/51/search_viewstat_1.txt', 'w+') as f1:
					f1.write(post_dynamic)
				with open('/data/fetch/task/51/hidCheckUserIds_1.txt', 'w+') as f2:
					f2.write(hidCheckUserIds)
				with open('/data/fetch/task/51/hidCheckKey_1.txt', 'w+') as f3:
					f3.write(hidCheckKey)
				with open('/data/fetch/task/51/hidValue_1.txt', 'w+') as f4:
					f4.write(hidValue)

				t2 = time.time() - t0
				loggers.info('update 51job id count:%s use time %s ' % (str(count_update), str(t2)))
				return True
		except Exception, e:
			logging.warn('update job51 id to redis %s' % str(e))
			loggers.warn('update job51 id to redis %s' % str(e))

	def update_zhilian(self):
		try:
			t0 = time.time()
			with open('/data/fetch/db/trans/zlsearch.html', 'r') as f_read:
				html = f_read.read()
			if html.find('valign="top"') > 0:
				soup = BeautifulSoup(html, 'html.parser')
				url_list = soup.select('.first-weight a')
				count_update = 0
				for i in url_list:
					id_info = i['href'].split('/')[-1] + '&t=' + i['onclick'].split(',')[1].strip("'") + '&k=' \
								+ i['onclick'].split(',')[2].split(';')[0].strip(')').strip("'")
					resume_id_key = self.mark_zhilian + i['tag'].replace('_1', '')
					if not self.r.get(resume_id_key):
						self.r.set(resume_id_key, id_info, ex=43200)
						count_update += 1
				t1 = time.time() - t0
				loggers.info('update zhilian id count:%s use time %s ' % (str(count_update), str(t1)))
				return True
		except Exception, e:
			loggers.warn('update zhilian id to redis %s' % str(e))

	def is_exist_id(self, flag, resume_id):
		try:
			if flag == 0:
				id_key = self.mark_51 + resume_id
			if flag == 1:
				id_key = self.mark_zhilian + resume_id
			id_info = self.r.get(id_key)
			if id_info:
				return id_info
			else:
				return False
		except Exception, e:
			logging.warn('check id in redis %s ' % str(e))
			loggers.warn('check id in redis %s ' % str(e))


class EventHandler(ProcessEvent):
	def process_IN_CREATE(self, event):
		print "Create file:%s." % os.path.join(event.path, event.name)

	def process_IN_DELETE(self, event):
		print "Delete file:%s." % os.path.join(event.path, event.name)

	def process_IN_MODIFY(self, event):
		print "Modify file:%s." % os.path.join(event.path, event.name)
		loggers.info("Modify file:%s." % os.path.join(event.path, event.name))
		search_update = SearchIdInfoUpdate()
		if event.name == 'search.html':
			search_update.update_job51()
		elif event.name == 'zlsearch.html':
			search_update.update_zhilian()


def FsMonitor(path='.'):
	wm = WatchManager()
	mask = IN_DELETE | IN_CREATE | IN_MODIFY
	notifier = Notifier(wm, EventHandler())
	wm.add_watch(path, mask, auto_add=True, rec=True)
	print "now starting monitor %s." % path
	loggers.info('now starting monitor %s' % path)

	while True:
		try:
			notifier.process_events()
			if notifier.check_events():
				print "check event true."
				loggers.info('check event true')
				notifier.read_events()
		except KeyboardInterrupt:
			print "keyboard Interrupt."
			notifier.stop()
			break


if __name__ == '__main__':
	FsMonitor('/data/fetch/db/trans/')
