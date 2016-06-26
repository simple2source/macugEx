# encoding: utf8

import common
from bs4 import BeautifulSoup
import logging, json, datetime, random, os, sys, collections, fileinput
import requests
reload(sys)
sys.setdefaultencoding('utf8')

# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir,\
	'huxiu.log')
logging.config.dictConfig(log_dict)
logging.info('start fetching article from huxiu')
sql_config = common.sql_config

headers = {
	'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9\
		,image/webp,*/*;q=0.8',
	'Accept-Encoding' : 'gzip, deflate, sdch',
	'Accept-Language' : 'zh-CN,zh;q=0.8',
	'Cache-Control' : 'max-age=0',
	'Connection' : 'keep-alive',
	'Host' : 'www.huxiu.com',
	'Referer' : 'http://www.huxiu.com/tagslist/4.html',
	'Upgrade-Insecure-Requests' : '1',
	'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36\
		 (KHTML, like Gecko) Chrome/50.0.2661.18 Safari/537.36'
}

s = requests.Session()
s.headers = headers
huxiu_hash_code = 'ad271569cd02c95887899d5545423397'
post_data = {
	'huxiu_hash_code' : huxiu_hash_code,
	'page' : '',
	'tag_id' : ''
}

def get_all_tags():
	tags_url = 'http://www.huxiu.com/tags'

	common.rand_sleep(5, 5)
	res = s.get(tags_url)
	res.encoding = "utf-8"
	soup = BeautifulSoup(res.text, 'html.parser')
	with open('temp.html', 'w') as f0:
		f0.write(res.text)
	tag_boxs = soup.find_all('div', class_='tag-cnt-box')
	with open('huxiu_tags.txt', 'w') as f:
		for box in tag_boxs:
			tags_list = box.find_all('li', class_='transition')
			for tag in tags_list:
				tag_id = tag.find('a').get('href').split('/')[-1].split('.')[0]
				tag_name = tag.find('a').get_text().encode('utf8').strip()
				# print tag_id, tag_name
				f.write(str(tag_id) + ':' + tag_name + '\n')

def get_article_num(tag_id):
	num = 0

	base_url = 'http://www.huxiu.com/tags/{}.html'.format(tag_id)
	api_url = 'http://www.huxiu.com/v2_action/tag_article_list'
	post_data['tag_id'] = tag_id
	page = 1

	try:
		post_data['page'] = page
		common.rand_sleep(5, 5)
		res = s.post(api_url, data=post_data)
		res_data = json.loads(res.text.encode('utf8'))
		total_page = res_data['total_page']
		if total_page == 1:
			common.rand_sleep(5, 5)
			res = s.get(base_url)
			res.encoding = "utf-8"
			soup = BeautifulSoup(res.text, 'html.parser')
			article_box = soup.find('div', class_='related-article')
			article_list = article_box.find_all('li')
			num = len(article_list)
		else:
			# 根据页数计算文章数
			num = 10*total_page
	except Exception, e:
		# print Exception, e
		logging.error('run error', exc_info=True)
		return num

	return num

def main():
	# 先获取所有的tags
	if not os.path.exists('huxiu_tags.txt'):
		get_all_tags()

	for line in fileinput.input('huxiu_tags.txt', inplace=1, backup='.bak'):
		items = line.split(':')
		# 当前行包含tag_id,tag_name,article_num，表示当前行抓取完成
		if len(items) == 3:
			new_line = line.replace('\n', '')
		else:
			tag_id = items[0]
			article_num = get_article_num(tag_id)
			new_line = line.replace('\n', '') + ':' + str(article_num)
		print new_line


if __name__ == '__main__':
	main()