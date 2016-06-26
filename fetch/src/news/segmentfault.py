# encoding: utf8

import common
from bs4 import BeautifulSoup
import logging, json, datetime, random, os, sys, collections, fileinput, re
import requests, urllib
reload(sys)
sys.setdefaultencoding('utf8')

# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir,\
	'segmentfault.log')
logging.config.dictConfig(log_dict)
logging.info('start fetching article from segmentfault')
sql_config = common.sql_config

headers = {
	'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9\
		,image/webp,*/*;q=0.8',
	'Accept-Encoding' : 'gzip, deflate, sdch',
	'Accept-Language' : 'zh-CN,zh;q=0.8',
	'Cache-Control' : 'max-age=0',
	'Connection' : 'keep-alive',
	# 'Host' : 'www.huxiu.com',
	# 'Referer' : 'http://www.huxiu.com/tagslist/4.html',
	# 'Upgrade-Insecure-Requests' : '1',
	'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36\
		 (KHTML, like Gecko) Chrome/50.0.2661.18 Safari/537.36'
}

s = requests.Session()
s.headers = headers

def get_article_num(tag_name):
	num = 0
	url = 'https://segmentfault.com/t/{}/blogs'.format(urllib.quote(tag_name))

	try:
		common.rand_sleep(5, 10)
		res = s.get(url)
		soup = BeautifulSoup(res.text, 'html.parser')
		pagination = soup.find('ul', class_='pagination')
		if pagination is None:
			article_list = soup.find_all('section', class_='stream-list__item')
			num = len(article_list)
		else:
			url += '?page=1000'
			common.rand_sleep(5, 10)
			res = s.get(url)
			soup = BeautifulSoup(res.text, 'html.parser')
			pagination = soup.find('ul', class_='pagination')
			total_page = pagination.find('li', class_='active').find('a').get_text()\
				.encode('utf8')
			num = int(total_page) * 15
	except Exception, e:
		logging.error('run error', exc_info=True)
		return num

	return num


def main():
	page = 1
	tag_url = 'https://segmentfault.com/tags/all?page={}'

	while 1:
		cur_url = tag_url.format(page)
		common.rand_sleep(5, 10)
		res = s.get(cur_url)
		soup = BeautifulSoup(res.text, 'html.parser')
		tags_list = soup.find_all('section', class_='tag-list__item')
		for tag_section in tags_list:
			tag_name = tag_section.find('h2').find('a').get_text()\
				.encode('utf8').strip()
			# 判断当前主题是否已经抓取完成
			with open('segmentfault_done.txt', 'r') as sdf:
				content = sdf.read()
				if content.find(','+tag_name+',') == -1:
					num = get_article_num(tag_name)
					with open('segmentfault_tags.txt', 'a') as stf:
						stf.write(tag_name+':'+str(num)+'\n')
				else:
					continue
			with open('segmentfault_done.txt', 'a') as f:
				f.write(','+tag_name)

		# 判断是否有下一页
		page += 1
		re_str = r'/tags/all\?page={}'.format(page)
		pat = re.compile(re_str)
		s_r = re.search(pat, res.text)
		if s_r is None:
			break
		else:
			continue


if __name__ == '__main__':
	main()