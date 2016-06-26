# encoding: utf8

import common
from bs4 import BeautifulSoup
import time, re, logging, json, MySQLdb, os, sys, datetime, random
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
	'tuicool2.log')
logging.config.dictConfig(log_dict)
logging.info('start fetching article from mux')
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

def make_dir(path):
	is_exists = os.path.exists(path)
	if not is_exists:
		os.makedirs(path)

def get_article(article_id, abs_file_path):
	'''获得文章，获取成功返回True，文章不在最近一周内返回False'''
	article_url = 'http://www.tuicool.com/articles/{}'.format(article_id)
	try:
		print article_url
		common.rand_sleep(5, 10)
		res = l.session.get(article_url)
		logging.info('return url {} success'.format(res.url))
		soup = BeautifulSoup(res.text, 'html.parser')
		title = str(soup.find('div', class_='article_detail_bg').find('h1')\
			.get_text())
		print title
		pub_time = re.sub(re.compile('时间[\s\S]{2}'), '', \
			str(soup.find('span', class_='timestamp').get_text()).strip())
		keywords = [str(item.get_text())\
			for item in soup.find_all('span', class_='new-label')]
		content = str(soup.find('div', class_='article_body'))

		# 只抓最近一周内的文章
		timedelta = datetime.date.today()-datetime.datetime\
			.strptime(pub_time, '%Y-%m-%d %H:%M:%S').date()
		if timedelta.days > 7:
			return False

		with open(abs_file_path, 'w') as f:
			f.write('标题：' + title + '\n')
			f.write('发布时间：' + pub_time + '\n')
			f.write('关键字：' + ', '.join(keywords) + '\n')
			f.write('内容：' + content + '\n')
		return True
	except Exception, e:
		print Exception, e
		logging.error('run error', exc_info=True)
		return False

def get_articles_in_topic(topic_id, topic_path):
	'''获得主题下的文章'''
	tp_base_url = 'http://www.tuicool.com/topics/{}'.format(topic_id)\
		+ '?st=0&lang=1&pn={}'
	
	# 判断当前主题是否已完成抓取
	if os.path.exists(topic_path + '/' + 'done'):
		print str(topic_id) + ': done'
		return

	page = 0
	
	while 1:
		try:
			cur_url = tp_base_url.format(page)
			print cur_url
			common.rand_sleep(5, 10)
			res = l.session.get(cur_url)
			with open('temp.html', 'w') as f:
				f.write(res.text.encode('utf8'))
			logging.info('return url {} success'.format(res.url))
			soup = BeautifulSoup(res.text, 'html.parser')

			# 获得文章列表
			articles_list = soup.find_all('div', class_='single_fake')
			for article in articles_list:
				article_id = str(article.find('a', class_='article-list-title')\
					.get('href').split('/')[2])
				article_title = str(article.find('a', class_='article-list-title')\
					.get_text()).strip()
				# 如果文章不存在
				abs_file_path = topic_path + '/' + article_id
				if not os.path.isfile(abs_file_path):
					# 取到的文章不符合要求，跳出当前主题
					if not get_article(article_id, abs_file_path):
						# 标记当前主题抓取完成
						with open(topic_path + '/' + 'done', 'w') as f:
							pass
						return
				else:
					continue

			# 判断是否有下一页
			page += 1
			cur_url = tp_base_url.format(page)
			re_str = r'/topics/{}\?st=0&lang=1&pn={}'.format(topic_id, page)
			pat = re.compile(re_str)
			s_r = re.search(pat, res.text)
			if s_r is None:
				# 标记当前主题抓取完成
				with open(topic_path + '/' + 'done', 'w') as f:
					pass
				break

		except Exception, e:
			print Exception, e
			logging.error('run error', exc_info=True)

l = Login('lijiacong86@163.com', 'Abc123!!')

def main():
	# 登录
	l.login()
	# 获得主题数据的api地址
	base_url = 'http://www.tuicool.com/topics/my_hot?id=1'
	make_dir(base_path)
	try:
		common.rand_sleep(5, 10)
		res = l.session.get(base_url)
		logging.info('return url {} success'.format(res.url))
		res_data = json.loads(res.text)		

		# 主题分类列表
		class_list = res_data['cats']
		for class_item in class_list:
			class_path = base_path + '/' + str(class_item['id'])\
				+ '_' + class_item['name'].encode('utf8')
			make_dir(class_path)
			# 主题列表
			topic_list = class_item['items']
			for topic in topic_list:
				topic_path = class_path + '/' + str(topic['id'])\
					+ '_' + topic['name'].encode('utf8')
				make_dir(topic_path)
				get_articles_in_topic(str(topic['id']), topic_path)

	except Exception, e:
		print Exception, e
		logging.error('run error', exc_info=True)

if __name__ == '__main__':
	main()