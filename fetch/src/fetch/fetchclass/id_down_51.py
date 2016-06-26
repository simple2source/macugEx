# -*- coding:utf-8 -*-

from lib51search import job51search
import sys,json,traceback,datetime,time,urllib,urlparse,logging,common,os,logging.config
from bs4 import BeautifulSoup
from extract_seg_insert import ExtractSegInsert
import RedisUpdateinfo


class IdDown51(job51search):
	def __init__(self, resume_id):
		job51search.__init__(self)
		self.resume_id = resume_id
		# log_file = '/data/fetch_git/fetch/src/fetch/log/input_id51.log'
		# fmt = '%(asctime)s %(filename)s %(funcName)s %(levelname)s Line:%(lineno)s :%(message)s'
		# logging.basicConfig(level=logging.DEBUG, filename=log_file,
		# 					format=fmt)
		# self.logger = logging.getLogger(__name__)
		with open(common.json_config_path) as f_log:
			f_read = f_log.read()
		log_dict = json.loads(f_read)
		log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'input_id_51.log')
		logging.config.dictConfig(log_dict)

	def get_id(self):
		try:
			# self.get_cookie()
			# html = open('/data/fetch/db/search.html', 'r').read()
			# soup = BeautifulSoup(html, 'html.parser')
			# url_list = soup.select('.SearchR a')
			flag = -10
			# url = None
			# for i in url_list:
			# 	if self.resume_id in i:
			# 		url = r'http://ehire.51job.com/' + i['href']
			# 		logging.info('id: %s html exist in local machine' % str(self.resume_id))
			# 		print 'id exist in local machine'
			# if not url:
			# 	flag = -11
			# 	logging.warn('---id: %s not exist in local' % str(self.resume_id))
			# 	return flag
			id_redis = RedisUpdateinfo.SearchIdInfoUpdate()
			id_info = id_redis.is_exist_id(0, self.resume_id)
			if not id_info:
				flag = -11
				logging.warn('---id: %s not exist in redis' % str(self.resume_id))
				return flag
			url = r'http://ehire.51job.com/' + id_info
			addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			prefixid = 'wu_' + str(self.resume_id)
			r = self.rp
			if r.rcheck(prefixid, addtime, 1):
				req_count = 0
				while req_count < 3:
					try:
						urlhtml = self.rand_get(url)
						isResume = self.isResume_chk(urlhtml)
						if isResume == -2:
							req_count = 0
							break
						elif isResume == -1:
							req_count = 3
						elif isResume == 0:
							self.get_cookie()
						elif isResume == 1:
							if self.save_resume(self.resume_id, urlhtml):
								r.tranredis('51search', 1, ext1=self.username, ext2='ok', ext3='')
								try:
									es_redis = r.es_check(prefixid)
									if es_redis == 0:
										data_back = ExtractSegInsert.fetch_do123(urlhtml, '51job', 1)
									elif es_redis == 1:
										data_back = ExtractSegInsert.fetch_do123(urlhtml, '51job', -1)
									print data_back, '++++++++ insert ++++++++',
									logging.info('id: %s insert success' % str(self.resume_id))
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
							flag = 8
							break
						elif isResume == 3:
							logging.info('resume id %s is removed by system' % str(self.resume_id))
							flag = 9
							break
						elif isResume == 4:
							logging.info('too more busy action and have a rest')
							flag = 10
							break
					except Exception, e:
						print traceback.format_exc(), e
			return flag
		except Exception, e:
			print traceback.format_exc(), e

if __name__ == '__main__':
	print 'id down 51 ------>>'