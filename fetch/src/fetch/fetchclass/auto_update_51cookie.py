# -*- coding:utf-8 -*-

from lib51search import job51search
import liblogin
import libaccount
import common
import json, os,time
import logging.config, logging

class UpdateCookie(job51search):
	def __init__(self):
		job51search.__init__(self)
		with open(common.json_config_path) as f_log:
			f_read = f_log.read()
		logger = logging.getLogger(__name__)
		log_dict = json.loads(f_read)
		log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'input_search.log')
		logging.config.dictConfig(log_dict)


	def insert_cookie(self):
		try:
			logging.info('update cookie start 333333 ........')
			redis_key_list = self.account.uni_user(time_period=self.time_period, num=self.time_num, hour_num=self.hour_num, day_num=self.day_num)
			print redis_key_list,00000000,'------'
			t0 = time.time()
			if len(redis_key_list) > 0:
				for redis_key in redis_key_list:
					flag = False
					while not flag:
						self.username = redis_key.split('_')[1].encode('utf-8')
						print self.username,1111111,'------'
						self.ck_str = self.account.redis_ck_get(self.username)
						print self.ck_str,222222,'-------'
						self.headers['Cookie'] = self.ck_str
						if self.login_status_chk():
							logging.info('cookie is useful {}'.format(self.username))
							flag = True
						else:
							sql_res = self.account.sql_password(self.username)
							print sql_res, '333333333', '----+++'
							self.account.redis_ck_ex(self.username)  # 更新该用户名的cookie失效时间
							self.password = sql_res[1]
							self.ctmname = sql_res[0].encode('utf-8')
							print self.password, self.username, self.ctmname, '444444444'
							l_login = liblogin.Login51(cn=self.ctmname, un=self.username, pw=self.password)
							self.ck_str = l_login.main(sleep=5)
							self.headers['Cookie'] = self.ck_str
							if self.login_status_chk():
								self.account.redis_ck_set(self.username, self.ck_str)
								logging.info('51job user {} auto login success'.format(self.username))
								logging.info('switching {} username {} success. '.format(self.module_name, self.username))
								flag = True
				t1 = str('%.2f' % (time.time() - t0)) + 's'
				logging.info('cookie update complete use time {}'.format(t1))
				return flag
			else:
				logging.error('no account lef for auto update 51 cookie')
				self.login2()
				return False

		except Exception, e:
			print e


if __name__=='__main__':
	app = UpdateCookie()
	app.insert_cookie()