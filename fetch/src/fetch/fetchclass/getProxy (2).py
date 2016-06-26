#-*- coding:UTF-8 -*-

import urllib2,time
from bs4 import BeautifulSoup
from random import choice
import traceback

class UseProxy():
	def __init__(self):
		self.address = ''
		self.sum_ip = ''

	def get_proxy(self):
		""" 从代理网站获取ip """
		try:
			url = r'http://www.xicidaili.com/nn/1'
			user_agent = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" \
						 " Chrome/43.0.2357.134 Safari/537.36"
			request = urllib2.Request(url)
			request.add_header("User-Agent", user_agent)
			ip_list = open('/data/fetch/database/ip_list.txt', 'w+')
			html = urllib2.urlopen(request)
			soup = BeautifulSoup(html, 'html.parser')
			trs = soup.select('tr')

			for i in range(1, len(trs)):
				ip_text = trs[i].get_text().strip().split('\n')
				ip_port = ip_text[0] + ':' + ip_text[1]
				self.sum_ip = self.sum_ip + ip_port + '-'
			ip_list.write(self.sum_ip)
			ip_list.close()

		except Exception, e:
			print e,traceback.format_exc()


	def random_ip(self):
		try:
			ip_list = open('/data/fetch/database/ip_list.txt', 'r').read()
			ip_list = ip_list.split('-')
			ip_list.pop()
			ip_list = ip_list[0:10]
			return ip_list
		except Exception, e:
			print e,traceback.format_exc()

if __name__ == '__main__':
	app = UseProxy()
	app.get_proxy()
	app.random_ip()