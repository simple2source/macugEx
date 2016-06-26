# -*- coding:utf-8 -*-

from libcjolsearch import *
from bs4 import BeautifulSoup
from extract_seg_insert import ExtractSegInsert
import traceback


class IdDowncjol(mainfetch):
	def __init__(self, resume_id):
		mainfetch.__init__(self)
		self.resume_id = resume_id
		self.refer = 'http://rms.cjol.com/SearchEngine/SearchResumeInCJOL.aspx'
		self.headers['Referer'] = self.refer
		self.headers['Host'] = 'rms.cjol.com'
		self.headers['Origin'] = 'http://rms.cjol.com'
		self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
		self.post_dict = {'Lang': 'CN', 'Fn': 'resume', 'bankid': '-1', 'JobSeekerID': ''}


	def get_id(self):
		try:
			self.get_cookie()
			url = r'http://rms.cjol.com/ResumeBank/Resume.aspx?JobSeekerID={}'.format(self.resume_id.strip('J'))
			addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			prefixid = 'c_' + str(self.resume_id.strip('J'))
			flag = -10
			r = self.rp
			print r.rcheck(prefixid, addtime), '-----------'
			if r.rcheck(prefixid, addtime):
				req_count = 0
				while req_count < 3:
					req_count += 1
					try:
						urlhtml = self.rand_get(url)
						isResume = self.isResume_chk(urlhtml)
						if isResume == -2:
							req_count = 0
						elif isResume == -1:
							req_count = 3
						elif isResume == 0:
							self.login2()
						elif isResume == 1:
							if self.save_resume(self.resume_id, urlhtml):
								r.tranredis('cjol', 1, ext1=self.username, ext2='ok', ext3='')
								try:
									es_redis = r.es_check(prefixid)
									if es_redis == 0:
										data_back = ExtractSegInsert.fetch_do123(urlhtml, 'cjol', 1)
									elif es_redis == 1:
										data_back = ExtractSegInsert.fetch_do123(urlhtml, 'cjol', -1)
									print data_back, '_______insert_________', 'url'
									ex_result = data_back[1]
									if ex_result == 1:
										flag = 1
										r.es_add(prefixid, addtime, 1)
									elif ex_result == -1:
										flag = -1
										r.es_add(prefixid, addtime, 1)
									elif ex_result == -4:
										flag = -4
										r.es_add(prefixid, addtime, 1)
									elif ex_result == 0:
										flag = 0
										r.es_add(prefixid, addtime, 1)
									elif ex_result == -2:
										flag = -2
										r.es_add(prefixid, addtime, 1)
									elif ex_result == -3:
										flag = -3
										r.es_add(prefixid, addtime, 1)
									elif ex_result == -5:
										flag = -5
										r.es_add(prefixid, addtime, 1)

									break
								except Exception, e:
									print traceback.format_exc(), e
						elif isResume == 2:
							logging.info('resume id %s is secret resume' % str(self.resume_id))
						elif isResume == 3:
							logging.info('resume id %s is removed by system' % str(self.resume_id))
						elif isResume == 5:
							logging.info('too more busy action and have a rest')

					except Exception, e:
						print traceback.format_exc(), e
			return flag
		except Exception, e:
			print traceback.format_exc(), e


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
					logging.info('get cjol username is {}'.format(self.username))
					# print(self.username), 99999999999
					self.ck_str = self.account.redis_ck_get(self.username)
					# print self.ck_str
					self.headers['Cookie'] = self.ck_str
					if self.login_status_chk():
						flag = True
						# print self.username * 100
						logging.info('switching {} username {} success. '.format(self.module_name, self.username))

				return flag
			else:
				logging.critical('no account left for {}'.format(self.module_name))
				return False
		except Exception, e:
			logging.critical('error msg is {}'.format(str(e)), exc_info=True)
			return False



if __name__ == '__main__':
	print 'id down cjol ----->'
	app = IdDowncjol('J8486220')
	app.get_id()


