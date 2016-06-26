# -*- coding:utf-8 -*-

from libzhilian import *
from bs4 import BeautifulSoup
from extract_seg_insert import ExtractSegInsert
import json,traceback,datetime,logging,logging.config
import RedisUpdateinfo


class IdDownzhilian(zhilianfetch):
	def __init__(self, resume_id):
		zhilianfetch.__init__(self)
		self.resume_id = resume_id
		self.address = '10.4.16.39:8888'
		with open(common.json_config_path) as f_log:
			f_read = f_log.read()
		log_dict = json.loads(f_read)
		log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'input_id_zhilian.log')
		logging.config.dictConfig(log_dict)

	def get_id(self):
		try:
			self.get_cookie()
			flag = -10
			# html = open('/data/fetch/db/zlsearch.html', 'r').read()
			# soup = BeautifulSoup(html, 'html.parser')
			# uplink = soup.select('.first-weight a')
			# url = None
			# for i in uplink:
			# 	if self.resume_id == i['tag'].replace('_1', ''):
			# 		logging.info('id: %s exist in local ' % str(self.resume_id))
			# 		url_part = r'http://rd.zhaopin.com/resumepreview/resume/viewone/2/'
			# 		url = url_part + i['href'].split('/')[-1] + '&t=' + i['onclick'].split(',')[1].strip("'") + '&k=' \
			# 		      + i['onclick'].split(',')[2].split(';')[0].strip(')').strip("'")
			# if not url:
			# 	flag = -11
			# 	logging.warn('--id %s not exist in local ' % str(self.resume_id))
			# 	return flag
			id_redis = RedisUpdateinfo.SearchIdInfoUpdate()
			id_info = id_redis.is_exist_id(1, self.resume_id)
			if not id_info:
				flag = -11
				logging.warn('---id: %s not exist in redis' % str(self.resume_id))
				return flag
			url = r'http://rd.zhaopin.com/resumepreview/resume/viewone/2/' + id_info
			addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			prefixid = 'z_' + self.resume_id
			r = self.rp
			if r.rcheck(prefixid, addtime, 1):
				req_count = 0
				while req_count < 3:
					try:
						post_data = 'searchKeyword='
						urlhtml = self.proxy_url_post(url, self.address, post_data)
						isResume = self.isResume_chk(urlhtml)
						if isResume == -2:
							req_count = 0
						elif isResume == -1:
							req_count = 3
						elif isResume == 0:
							self.login2()
						elif isResume == 1:
							if self.save_resume(self.resume_id, urlhtml):
								r.tranredis('zhilian', 1, ext1=self.username, ext2='ok', ext3='')
								try:
									es_redis = r.es_check(prefixid)
									if es_redis == 0:
										data_back = ExtractSegInsert.fetch_do123(urlhtml, 'zhilian', 1)
									elif es_redis == 1:
										data_back = ExtractSegInsert.fetch_do123(urlhtml, 'zhilian', -1)
									print data_back, '_______insert_________'
									logging.info('%s insert success ' % str(self.resume_id))
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
							break
						elif isResume == 3:
							logging.info('resume id %s is removed by system' % str(self.resume_id))
							break
						elif isResume == 5:
							logging.info('too more busy action and have a rest')
							break

					except Exception, e:
						print traceback.format_exc(), e
			return flag
		except Exception, e:
			print traceback.format_exc(), e

if __name__ == '__main__':
	print 'id down zhilian ----->'



