# -*- coding:utf-8 -*-

import os, json ,re,time
from extract_seg_insert import ExtractSegInsert
from elasticsearch import Elasticsearch
import traceback


# class zhilian_excption(object):
# 	def __init__(self):
# 		self.size = 100
# 		self.es = Elasticsearch("183.131.144.102:8090")
# 		self.res = self.es.search(index='resume', doc_type='doc', scroll='1m', size=self.size,
# 								  _source_include=["resume_id"], body=
# 								  {
# 									  "query": {"match_all": {}}
# 								  }
# 								  )
# 		self.scroll_id = self.res['_scroll_id']
#
# 	def exception_check(self):
# 		try:
# 			degree_list = [u'初中', u'高中', u'大专', u'本科', u'硕士', u'MBA', u'EMBA', u'博士', '']
# 			for i in range(0, 10):
# 				res = self.es.scroll(scroll_id=self.scroll_id, scroll='1m')
# 				scroll_id = res['_scroll_id']
# 				print scroll_id, '+++++'
# 				for j in res['hits']['hits']:
# 					if j['_source']:
# 						for k in j['_source']['resume_id']:
# 							resume_id = k['resume_id']
# 							if resume_id not in degree_list:
# 								print resume_id
# 		except Exception, e:
# 			print Exception, e

# '''遍历搜索库异常的简历,写到本地文件,记录简历Id'''
# size = 100
# es = Elasticsearch("183.131.144.102:8090")
# res = es.search(index='supin_resume', doc_type='doc_v1', scroll='1m', size=size,
# 			   _source_include=[ "id",'education.degree'], body=
# 			   {
# 				   "query": {"match_all": {}}
# 			   }
# 			   )
# scroll_id = res['_scroll_id']
# # print scroll_id
# record = 0
# seg = 0
# count = 0
# acor = 0
# # print res
# for i in range(0, 20000):
# 	degree_list = [u'初中', u'中专', u'中技', u'其他', u'初中及以下',u'高中', u'大专', u'本科', u'硕士', u'MBA', u'EMBA', u'博士', '']
# 	res = es.scroll(scroll_id=scroll_id, scroll='1m')
# 	af_list = res['hits']['hits']
# 	# print af_list,len(af_list)
# 	# print res['hits']['hits'][0]['_source']['degree'],res['hits']['hits'][0]['_source']['id'] ,'++++'
# 	scroll_id = res['_scroll_id']
# 	for j in res['hits']['hits']:
# 		try:
# 			seg += 1
# 			f3 = open('resume_id4.txt', 'a+')
# 			f3.write(j['_source']['id']+'\n')
# 			f3.close()
# 			print seg,j['_source']['id']
# 			try:
# 				if j['_source']['education'][0]['degree'] not in degree_list:
# 					print j['_source']['education'][0]['degree'],'++++',j['_source']['id']
# 					record += 1
# 					a = j['_source']['id'] + '-' + j['_source']['education'][0]['degree']
# 					f = open('exception_zhilian4.txt', 'a+')
# 					f.write(a+'*'+str(record)+'\n')
# 					time.sleep(0.5)
# 					f.close()
# 				elif j['_source']['education'][0]['degree']  in degree_list:
# 					b = j['_source']['id'] + '-' +j['_source']['education'][0]['degree']
# 					acor += 1
# 					f1= open('coret_zhilian4.txt', 'a+')
# 					f1.write(b+'*'+str(acor)+'\n')
# 					f1.close()
# 				elif not j['_source']:
# 					count = 0+1
# 					f2=open('done.txt','a+')
# 					f2.write(str(count)+'\n')
# 			except Exception,e:
# 				print Exception,e
# 		except Exception,e:
# 			print 'errr----'
# 			pass


'''遍历记录在本地文件异常简历id,并覆盖搜索库异常简历'''
seg = 0
count = 0
error = 0
no_exist = 0
for m in open('exception_zhilian4.txt', 'r+').readlines():
	try:
		resume_id = m.split('-')[0]
		count += 1
		resume_file = resume_id  +'.html'
		resume_path = '/data/fetch_git/fetch/src/fetch/db/zhilian/' + resume_id[0:3] + '/' + resume_id[3:6] + '/'
		print count,'----->',resume_id,resume_path
		if resume_file in os.listdir(resume_path):
			try:
				resume_html = open(resume_path+resume_file).read()
				data_back = ExtractSegInsert.fetch_do123(resume_html,'zhilian', -1)
				result = data_back[1]
				if result == -1:
					seg += 1
					print seg,'+++++',result,resume_id
					with open('su_cover.txt', 'a+') as f:
						f.write(resume_id+'-'+str(seg)+'\n')
				else:
					error += 1
					with open('fail_cover.txt','a+') as f1:
						f1.write(resume_id+'-'+str(error)+'\n')
			except Exception,e:
				print traceback.format_exc()
				print e
		else:
			no_exist += 1
			with open('no_zhilian_exist.txt', 'a+') as f2:
				f2.write(resume_id+'-'+str(no_exist)+'\n')

	except Exception,e:
		print e
		# print traceback.format_exc()