# -*- coding:utf-8 -*-

import os,sys,datetime
# from extract_seg_insert import ExtractSegInsert
import extract_buyed
import oldmysql
from redispipe import *

resume_path = '/data/51job_oldbuy/51job'


def traversal_resume(resume_path):
	try:
		for resume in os.listdir(resume_path):
			resume_id = resume.split('.')[0]
			resume = os.path.join(resume_path, resume)
			html = open(resume, 'r+').read()
			prefixid = 'wu_' + resume_id
			if html.find('电　话：') > 0:
				print resume_id
				try:
					resume_dict = extract_buyed.extract_51_buy(content=html)
					seged_dict = extract_buyed.new_seg_buy(resume_dict)
					app = oldmysql.OldMysql('51job', seged_dict)
					app.run_work()
				except Exception, e:
					print Exception, str(e), resume_id, 11111111111111

	except Exception, e:
		print e

traversal_resume(resume_path)
print 'done-------------'
