# -*- coding:utf-8 -*-

from lib51search import job51search
import sys,json,traceback,datetime,time,urllib
from bs4 import BeautifulSoup
import cgi


class TransportSearch(job51search):
	def __init__(self):
		job51search.__init__(self)
		self.host = r'ehire.51job.com'
		self.login_wait = 300
		self.refer = ''
		self.post_data_first = open('/data/fetch/task/51/post_viewstat.txt', 'r').read()

		self.convert_area = {'北京': '010000', '上海': '020000', '广州': '030200', '深圳': '040000', '7C000000': '7C000000'}
		self.convert_year = {'在读学生': '7C1%7C1', '应届毕业生': '7C2%7C2', '1-2年': '7C3%7C3', '2-3年': '7C4%7C4',
		'3-4年': '7C5%7C5', '5-7年': '7C6%7C6', '8-9年': '7C7%7C7', '10年以上': '7C8%7C99', '7C99': '7C99'}
		self.convert_degree = {'大专': '7C5', '本科': '7C6', '硕士': '7C7', '硕士以上': '7C8', '7C99': '7C99'}
		self.keyword = {}
		self.page_num = '1'


	def get_post_viewstat(self):
		try:
			self.login2()
			url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
			hidWhere = r'hidWhere=00%230%230%230%7C99%7C20150826%7C20160226%7C99%7C99%7C3%7C3%7C99%7C000000%7C010000%7C99%7C99%7C99%7C0000%7C6%7C6%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C000000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23php'
			hidWhere = hidWhere.replace('20160226', time.strftime('%Y%m%d', time.localtime())).replace('20160218', (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d'))
			self.post_data_first = self.post_data_first + hidWhere
			html = None
			while not html:
				html = self.url_post(url, self.post_data_first)
				soup = BeautifulSoup(html, 'html.parser')
				post_dynamic = soup.select('#__VIEWSTATE')[0]['value']
				post_dynamic = urllib.quote_plus(post_dynamic)
				hidCheckUserIds = soup.select('#hidCheckUserIds')[0]['value']
				hidCheckUserIds = urllib.quote_plus(hidCheckUserIds)
				hidCheckKey = soup.select('#hidCheckKey')[0]['value']
				hidCheckKey = urllib.quote_plus(hidCheckKey)
				hidValue = soup.select('#hidValue')[0]['value']
				hidValue = urllib.quote_plus(hidValue)
				with open('/data/fetch/task/51/search_viewstat.txt', 'w+') as f1:
					f1.write(post_dynamic)
				with open('/data/fetch/task/51/hidCheckUserIds.txt', 'w+') as f2:
					f2.write(hidCheckUserIds)
				with open('/data/fetch/task/51/hidCheckKey.txt', 'w+') as f3:
					f3.write(hidCheckKey)
				with open('/data/fetch/task/51/hidValue.txt', 'w+') as f4:
					f4.write(hidValue)
				print self.post_data_first
				print 'record viewstat +++++++++++++'
		except Exception, e:
			print e, traceback.format_exc()



	def run_crawl(self,area='',year='',age='',degree='',keyword='',page_num='1'):
		try:
			self.get_post_viewstat()
			get_viewstat = open('/data/fetch/task/51/search_viewstat.txt', 'r+').read()
			post_main = open('/data/fetch/task/51/post_mainmenu.txt', 'r+').read()
			hidCheckUserIds = open('/data/fetch/task/51/hidCheckUserIds.txt', 'r+').read()
			hidCheckKey = open('/data/fetch/task/51/hidCheckKey.txt', 'r+').read()
			url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
			hidValue='KEYWORDTYPE%230*LASTMODIFYSEL%235*AGE%2324%7C24*WORKYEAR%238%7C8*AREA%23020000*TOPDEGREE%236%7C6*KEYWORD%23php&'
			hidWhere = r'hidWhere=00%230%230%230%7C99%7C20160218%7C20160225%7C99%7C99%7C4%7C4%7C99%7C000000%7C030200%7C99%7C99%7C99%7C0000%7C1%7C1%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C000000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23php&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0'
			self.post_data_input = '__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=' + get_viewstat + post_main
			hidWhere = hidWhere.replace('20160225', time.strftime('%Y%m%d', time.localtime())).replace('20160218', (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d'))




			if keyword:
				self.post_data_input = self.post_data_input.replace('php', keyword)
				hidValue = hidValue.replace('php', keyword)
				hidWhere = hidWhere.replace('php', keyword)
			else:
				self.post_data_input = self.post_data_input.replace('php', '')
				hidWhere = hidWhere.replace('php', '')

			if area:
				area_quote = urllib.quote_plus(area)
				self.post_data_input = self.post_data_input.replace('%E5%8C%97%E4%BA%AC', area_quote)
				self.post_data_input = self.post_data_input.replace('030200', self.convert_area[area])
				hidValue = hidValue.replace('030200', self.convert_area[area])
				hidWhere = hidWhere.replace('030200', self.convert_area[area])
			else:
				area_quote = urllib.quote_plus('选择/修改')
				self.post_data_input = self.post_data_input.replace('%E5%8C%97%E4%BA%AC', area_quote)
				hidValue = hidValue.replace('*AREA%23020000', '')

			if year:
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24WorkYearFrom=3'[-1], self.convert_year[year][-1])
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24WorkYearTo=3'[-1], self.convert_year[year][-1])
				hidValue = hidValue.replace('8', self.convert_year[year][-1])
				hidWhere = hidWhere.replace('7C4%7C4', self.convert_year[year])

			if age:
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24AgeFrom=24'[-2:], age)
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24AgeTo=24'[-2:], age)
				hidValue = hidValue.replace('24', age)
			else:
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24AgeFrom=24'[-2:], '')


			if degree:
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24TopDegreeFrom=6'[-1], self.convert_degree[degree][-1])
				self.post_data_input = self.post_data_input.replace('ctrlSerach%24TopDegreeTo=6'[-1], self.convert_degree[degree][-1])
				hidValue = hidValue.replace('6', self.convert_degree[degree][-1])
				hidWhere = hidWhere.replace('7C1', self.convert_degree[degree])

			self.post_data_input = self.post_data_input.replace('340639802%2C339976831%2C336491451%2C322609757%2C340597700%2C336934384%2C339939576%2C338455211%2C339734907%2C324496708%2C319174609%2C338601384%2C339463451%2C338619719%2C338888440%2C319984937%2C319041317%2C338578441%2C339759897%2C324082201%2C340572035%2C339052082%2C316282573%2C340565258%2C325012156%2C88793201%2C340366224%2C55955168%2C318361092%2C336085991%2C339051440%2C340006397%2C339707788%2C339070187%2C339983845%2C327842852%2C335294406%2C339047846%2C322887540%2C340361983%2C333096045%2C323729275%2C326969192%2C334425050%2C315080650%2C340319412%2C336180534%2C338434683%2C339878421%2C338480953', hidCheckUserIds)
			self.post_data_input = self.post_data_input.replace('3659535d6efb8dfe850b66b9b406150c', hidCheckKey)

			self.post_data_input = self.post_data_input.replace('125', page_num)
			self.post_data_input = self.post_data_input + hidValue + hidWhere
			html = None
			while not html:
				html = self.url_post(url, self.post_data_input)
				if html.find('id="Login_btnLoginCN"') > 0:
					self.login()
			f = open('input.html', 'w+')
			f.write(html)
			f.close()
			print self.post_data_input
			html = json.dumps(html)
			print '++++++++++++'
			return html

		except Exception, e:
			print e, traceback.format_exc()


if __name__ == '__main__':
	# form = cgi.FieldStorage()
	# area = form['area'].value
	# year = form['year'].value
	# degree = form['degree'].value
	# keyword = form['keyword'].value
	# page_num = form['page_num'].value
	appfetch = TransportSearch()
	result =appfetch.run_crawl(area='上海',year='1-2年',age='',degree='本科',keyword='java',page_num='1')
