# encoding: utf8

import common
from bs4 import BeautifulSoup
import time, re, logging, json, MySQLdb, os, sys, datetime, random, collections
from readability.readability import Document
import requests
reload(sys)
sys.setdefaultencoding('utf8')

# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir,\
	'tuicool.log')
logging.config.dictConfig(log_dict)
logging.info('start fetching article from tuicool')
sql_config = common.sql_config
base_path = '/data/fetch/src/news/tuicool'

class Login():
	'''登录对象，提供登录推酷、检查登录状态的方法和已登录的会话对象'''
	def __init__(self, email='', password=''):
		self.session = requests.Session()
		self.req_params = {
			'email' : email,
			'password' : password,
			'remember' : '1',
		}
		self.header = {
            'Accept': "text/html,application/xhtml+xml,application/xml;\
            	q=0.9,image/webp,*/*;q=0.8",
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control' : 'max-age=0',
            'Connection': 'keep-alive',
            'If-None-Match' : 'W/"8f23c2a9d34b2c06b06baa6d7dcd8681"',
            'Upgrade-Insecure-Requests' : '1',
            'Host': 'www.tuicool.com',
            'Referer': 'http://www.tuicool.com/a/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36\
            	 (KHTML, like Gecko) Chrome/50.0.2661.18 Safari/537.36',
		}
		self.session.headers = self.header
		self.url = 'http://www.tuicool.com/login'
		self.email = email
		self.password = password
		self.cookie_str = ''
		self.proxies = {
			'http' : 'http://45.32.46.224:3128'
		}

	def login(self):
		'''返回cookie_str'''
		# 先获得authenticity_token
		common.rand_sleep(5, 10)
		res = self.session.get(self.url)
		soup = BeautifulSoup(res.text, 'html.parser')
		authenticity_token = soup.find('meta', attrs={'name': 'csrf-token'})\
			['content']
		print 'authenticity_token: ' + authenticity_token
		self.req_params['authenticity_token'] = authenticity_token

		# 使用用户名密码模拟登录
		common.rand_sleep(5, 10)
		res = self.session.post(self.url, data=self.req_params,\
			verify=False)
		cookie = requests.utils.dict_from_cookiejar(self.session.cookies)
		cookie_str = "; ".join([str(x)+"="+str(y) for x, y in cookie.items()])
		self.cookie_str = cookie_str
		self.session.headers['Cookie'] = cookie_str
		print 'cookie_str: ' + cookie_str
		return cookie_str

def count_articles_in_topic(topic_id):
	'''计算主题下一周内的文章数量'''
	result = 0
	tp_base_url = 'http://www.tuicool.com/topics/{}'.format(topic_id)\
		+ '?st=0&lang=1&pn={}'

	page = 0
	
	while 1:
		try:
			cur_url = tp_base_url.format(page)
			print cur_url
			common.rand_sleep(5, 10)
			res = l.session.get(cur_url)
			logging.info('return url {} success'.format(res.url))
			soup = BeautifulSoup(res.text, 'html.parser')

			# 获得文章列表
			articles_list = soup.find_all('div', class_='single_fake')
			for article in articles_list:
				article_id = str(article.find('a', class_='article-list-title')\
					.get('href').split('/')[2])
				article_title = str(article.find('a', class_='article-list-title')\
					.get_text()).strip()
				pub_time = str(article.find('div', class_='meta-tip')\
					.find_all('span')[1].get_text()).strip()
				if pub_time.find('201') == -1:
					pub_time = '2016-' + pub_time + ':00'
				else:
					return result
				# 判断时间是否在一周内
				timedelta = datetime.date.today()-datetime.datetime\
					.strptime(pub_time, '%Y-%m-%d %H:%M:%S').date()
				if timedelta.days <= 7:
					result += 1
				else:
					return result

			# 判断是否有下一页
			page += 1
			cur_url = tp_base_url.format(page)
			re_str = r'/topics/{}\?st=0&lang=1&pn={}'.format(topic_id, page)
			pat = re.compile(re_str)
			s_r = re.search(pat, res.text)
			if s_r is None:
				return result

		except Exception, e:
			print Exception, e
			logging.error('run error', exc_info=True)

	return result

l = Login('362598868@qq.com', 'Abc123!!')

def main():
	# 登录
	l.login()
	# 获得主题数据的api地址
	base_url = 'http://www.tuicool.com/topics/my_hot?id=1'
	try:
		common.rand_sleep(5, 10)
		res = l.session.get(base_url)
		logging.info('return url {} success'.format(res.url))
		res_data = json.loads(res.text)		

		result = {}

		# 主题分类列表
		class_list = res_data['cats']
		with open('articles_count0.txt', 'w') as f0:
			for class_item in class_list:
				class_id_name = str(class_item['id'])\
					+ '_' + class_item['name'].encode('utf8')
				# 主题列表
				topic_list = class_item['items']
				for topic in topic_list:
					topic_id_name = class_id_name + '_' + str(topic['id'])\
						+ '_' + topic['name'].encode('utf8')
					num = count_articles_in_topic(str(topic['id']))
					result[topic_id_name] = num
					print topic_id_name, num
					f0.write(topic_id_name + ': ' + str(num) + '\n')
		# 按主题名排序
		result = collections.OrderedDict(sorted(\
			result.items(), key = lambda t: t[0]))
		with open('articles_count.txt', 'w') as f:
			for topic_id, num in result.iteritems():
				f.write(topic_id + ': ' + str(num) + '\n')

	except Exception, e:
		print Exception, e
		logging.error('run error', exc_info=True)

if __name__ == '__main__':
	main()