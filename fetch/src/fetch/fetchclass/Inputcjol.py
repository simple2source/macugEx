# -*- coding:UTF-8 -*-
import json,urllib2
from libcjolsearch import *
from bs4 import BeautifulSoup
import logging.config
import common
import traceback
import logging




class TransportCjol(mainfetch):
	def __init__(self):
		mainfetch.__init__(self)
		self.get_dict = {'fn': 'd'}
		self.refer = 'http://newrms.cjol.com/SearchEngine/List?fn=d'
		self.headers['Referer'] = self.refer
		self.headers['Host'] = 'newrms.cjol.com'
		self.headers['Origin'] = 'http://newrms.cjol.com'
		self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
		self.post_dict = {'GetListResult': 'GetListResult', 'PageSize': '40', 'Sort': 'UpdateTime desc', 'PageNo': '1'}
		self.convert_area = {u'北京': '31', u'上海': '30', u'广州': '2010', u'深圳': '2008'}
		self.convert_degree = {u'大专': '50', u'本科': '60', u'硕士': '70', u'中专': '40', u'博士': '80'}
		self.convert_industry = {u'互联网/电子商务/网游': '7008', u'计算机软件及服务': '7180'}
		self.work_func = {u'计算机软件类': '0102', u'测试类': '0103'}



		with open(common.json_config_path) as f_log:
			f_read = f_log.read()
		logger = logging.getLogger(__name__)
		log_dict = json.loads(f_read)
		log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'input_cjol.log')
		logging.config.dictConfig(log_dict)



	def crawl_cjol(self, area=None, year=None, age=None, degree=None,
					keyword=None, industry=None, work_func=None, job_area=None, updatetime='93', page_num='1'):
		try:
			logging.info('start crawl cjol search 000000-----')
			t0 = time.time()

			self.get_cookie()
			url = r'http://newrms.cjol.com/SearchEngine/List?'
			t2 = time.time() - t0
			logging.info('load cookie use time %s s.......' % str(t2))

			if keyword:
				self.get_dict['Keyword'] = keyword

			if area:
				self.get_dict['CurrentLocation'] = self.convert_area[area]

			if year:
				self.get_dict['MinWorkExperience'] = year
				self.get_dict['MaxWorkExperience'] = str(int(year) + 2)

			if age:
				self.get_dict['MinAge'] = age
				self.get_dict['MaxAge'] = age

			if degree:
				self.get_dict['MinEducation'] = degree
				self.get_dict['MaxEducation'] = degree

			if industry:
				self.get_dict['CurrentIndustry'] = industry

			if work_func:
				self.get_dict['CurrentJobFunction'] = work_func

			if job_area:
				self.get_dict['ExpectedLocation'] = job_area

			if updatetime:
				self.get_dict['UpdateTime'] = updatetime

			if page_num:
				self.post_dict['PageNo'] = page_num

			get_url = urllib.urlencode(self.get_dict)
			url = url + get_url
			post_data = urllib.urlencode(self.post_dict)

			html = None
			while not html:
				html = self.rand_post(url, post_data)
				if html.find('招聘管理系统登录') > 0:
					self.login2()
					html = None
			print url, '------->', post_data
			with open('/data/fetch/db/cjolsearch.html', 'w+') as f:
				f.write(html)

			try:
				soup = BeautifulSoup(html, 'html.parser')
				resume_count = soup.select('#hid_search_total_count')[0]['value']
				page_count = soup.select('#hid_search_page_count')[0]['value']
				show_list = soup.select('.clearfix')
			except Exception, e:
				print traceback.format_exc(), e
				logging.error('fetch return html error ----')

			html_array = {'resume_list': '', 'page_count': ''}
			resume_list = []
			i = 0
			while i < len(show_list):
				html_dict = {'id': '', 'age': '', 'gender': '', 'resume_update': '', 'degree': '', 'year': '', 'area': '', 'function': ''}
				html_dict['id'] = show_list[i].get_text().strip().split('\n')[0].strip('J')
				html_dict['gender'] = show_list[i].get_text().strip().split('\n')[1]
				html_dict['age'] = show_list[i].get_text().strip().split('\n')[2]
				html_dict['degree'] = show_list[i].get_text().strip().split('\n')[3]
				html_dict['year'] = show_list[i].get_text().strip().split('\n')[4]
				html_dict['area'] = show_list[i].get_text().strip().split('\n')[5]
				html_dict['function'] = show_list[i].get_text().strip().split('\n')[6]
				html_dict['resume_update'] = show_list[i].get_text().strip().split('\n')[7]
				resume_list.append(html_dict)
				i += 1
				if i % 2 == 1:
					i += 1


			html_array['resume_list'] = resume_list
			html_array['resume_count'] = resume_count
			html_array['page_count'] = page_count

			html_array = json.dumps(html_array)
			t1 = time.time()-t0
			logging.info('finish search return use time %s .....' % str(t1))
			print '**********----END-----*******'
			return html_array




		except Exception, e:
			print traceback.format_exc(), e
			logging.error('search error fetch fail----')

	def get_cookie(self):    # 更改这里参数来选择账号
		try:
			flag = False
			redis_key_list = self.account.uni_user(time_period=self.time_period, num=self.time_num, hour_num=self.hour_num, day_num=self.day_num)
			# print redis_key_list, 8888888888
			if len(redis_key_list) > 0:
				while len(redis_key_list) > 0 and not flag:
					redis_key = redis_key_list[0]
					redis_key_list.remove(redis_key)
					self.username = redis_key.split('_')[1]
					logging.info('cjol username  is {}'.format(self.username))
					# print(self.username), 99999999999
					self.ck_str = self.account.redis_ck_get(self.username)
					# print self.ck_str
					self.headers['Cookie'] = self.ck_str
					flag = True
					# if self.login_status_chk():
					# 	flag = True
					# 	print self.username * 100
					# 	logging.info('switching {} username {} success. '.format(self.module_name, self.username))

				return flag
			else:
				logging.critical('no account left for {}'.format(self.module_name))
				return False
		except Exception, e:
			logging.critical('error msg is {}'.format(str(e)), exc_info=True)
			return False




if __name__ == '__main__':
	# TransportCjol().crawl_cjol('深圳', '3', 'None', '60', 'java', '7008', 'None', 'None', '62', '2')
	print 'cjol---------'
