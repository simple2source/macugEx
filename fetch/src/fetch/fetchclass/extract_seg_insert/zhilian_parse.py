#-*- coding:utf-8 -*-


# from BaseFetch import BaseFetch
from bs4 import BeautifulSoup
import json, re, sys, traceback,time,os,string

class zhilian_parse(object):
	"""docstring for zhilian_parse"""
	def __init__(self):
		# super(zhilian_parse, self).__init__()
		# self.resume_file = resume
		self.extract = {'resume_update_time':'','resume_name':'','id':'','target_functions':'','sex':'','age':'','work_seniority':'','degree':'','marital_status':'','domicile':',','political_status':'','household':'','job_status':'','expected_city':'','expected_salary':'','job_type':'','expect_work':'','expected_industry':'', 'work_experience': [],'project': [],'education': [],'self_evaluation': [],'language_skill': [],'skill': [],'graduate_time':'','certificate':[],'train':[],'birthday':'','school':'','major':'','start_work_time': 0, 'name': '', 'telephone': '', 'email': ''}



	def run_parse(self, html):
		'''运行简历解析'''
		try:
			# html = open(self.resume_file,'r+').read()
			soup = BeautifulSoup(html,'html.parser')
			if html.find('简历名称') > 0:
				resume_name = soup.select('#resumeName')[0].get_text()
				self.extract['resume_name'] = resume_name
			if html.find('简历更新时间') > 0:
				resume_update_time = soup.select('#resumeUpdateTime')[0].get_text()
				# resume_update_time = re.search(r'[>^].*[<$]',resume_update_time).group()
				resume_update_time = resume_update_time.replace(u'年', '-').replace(u'月', '-').replace(u'日','')
				self.extract['resume_update_time'] = resume_update_time
			if html.find('resume-left-tips-id') > 0:
				id = soup.select('.resume-left-tips-id')[0].get_text()
				id = id.strip('ID:')
				self.extract['id'] = id
			if html.find('desireIndustry') > 0:
				target_functions = soup.select('#desireIndustry')[0].get_text()
				# target_functions = re.search(r'[>^].*[<$]',target_functions).group()
				# target_functions = target_functions.strip('>').rstrip('<')
				self.extract['target_functions'] = target_functions
			if html.find('summary-top') > 0:
				summary_top = soup.select('.summary-top')[0].get_text().strip()
				political_common = [u'中共党员(含预备党员)',u'团员', u'群众', u'民主党派', u'无党派人士']
				marital_common = [u'未婚',u'已婚',u'离异']
				degree_common = [u'初中', u'中技', u'高中', u'中专', u'大专', u'本科', u'硕士', u'博士', u'MBA', u'EMBA']
				summary_top_list = summary_top.split()
				self.extract['sex'] = summary_top_list[0]
				self.extract['age'] = summary_top_list[1][:2]
				age_birthday = summary_top_list[1]
				self.extract['birthday'] = re.search('[(^].*[$)]', age_birthday).group().strip('(').rstrip(')')
				if summary_top.find(u'工作经验') >0:
					self.extract['work_seniority'] = summary_top_list[2]
					self.extract['start_work_time'] = int(time.strftime('%Y', time.localtime(time.time()))) - int(summary_top_list[2].replace(u'年工作经验',''))
				# 	self.extract['degree'] = summary_top_list[3]
				# 	if summary_top.find(u'婚')>0 or summary_top.find(u'离异')>0:
				# 		self.extract['domicile'] = summary_top_list[5].replace(u'现居住地：','')
				# 		if summary_top.find(u'户口'):
				# 			self.extract['household'] = summary_top_list[7].replace(u'户口：','')
				# 	else:
				# 		self.extract['domicile'] = summary_top_list[4].replace(u'现居住地：','')
				# else:
				# 	self.extract['degree'] = summary_top_list[2]
				# 	if summary_top.find(u'婚')>0 or summary_top.find(u'离异')>0:
				# 		self.extract['domicile'] = summary_top_list[4].replace(u'现居住地：','')
				# 	else:
				# 		self.extract['domicile'] = summary_top_list[3].replace(u'现居住地：','')

				if summary_top.find(u'现居住地') > 0:
					domicile = soup.select('.summary-top')[0].get_text().strip().split('\n')[2].split('|')[0].replace(u'现居住地：','').strip()
					self.extract['domicile'] = domicile

				if summary_top.find(u'户口') > 0:
					household = soup.select('.summary-top')[0].get_text().strip().split('\n')[2].split('|')[1].replace(u'户口：','').strip()
					self.extract['household'] = household

				for degree in degree_common:
					if degree in summary_top:
						self.extract['degree'] = degree
				for political_status in political_common:
					if political_status in summary_top:
						self.extract['political_status'] = political_status
				for marital_status in marital_common:
					if marital_status in summary_top:
						self.extract['marital_status'] = marital_status

			if html.find('resume-preview-main-title') > 0:
				if soup.select('.resume-preview-main-title')[0].get_text().strip() != '个人信息':
					self.extract['name'] = soup.select('.resume-preview-main-title')[0].get_text().strip()

			if html.find('feedbackD02') > 0:
				self.extract['telephone'] = soup.select('em')[0].get_text()
				self.extract['email'] = soup.select('em')[1].get_text()

			if html.find('resume-preview-top') > 0:
				'''求职意向'''
				resume_preview_top = soup.select('.resume-preview-top')[0].get_text().split()
				self.extract['expected_city'] = resume_preview_top[1]
				self.extract['expected_salary'] = resume_preview_top[3]
				self.extract['job_status'] = resume_preview_top[5]
				self.extract['job_type'] = resume_preview_top[7]
				self.extract['expected_industry'] = resume_preview_top[11]



			if html.find('自我评价') > 0:
				self_evaluation = soup.select('.rd-break')[0].get_text()
				self.extract['self_evaluation'] = self_evaluation


				'''抽取项目经历'''
			project = []
			project_soup = ''
			if html.find('项目经历') > 0:
				resume_all = soup.select('.resume-preview-all')
				for i in resume_all:
					if i.get_text().find(u'项目经历') > 0:
						project_soup = i
				seg = 0
				for x in project_soup.select('h2'):
					project_dict = {'project_time':'','project_name':'','project_describe':''}
					project_common = project_soup.select('h2')[seg].get_text()
					duty_describe = ''
					project_describe = ''
					if len(project_common.split()) >3:
						# project_time = re.search('[\d]{4}.[\d]{2}.*[\d]{4}.[\d]{2}',project_common).group()
						project_time = project_common[0:19]
						project_name = project_common[19:]

					project_content = project_soup.select('.resume-preview-dl')[seg].get_text()
					if project_content.find(u'责任描述') >0 and project_content.find(u'项目描述') <0:
						duty_describe = project_soup.select('.resume-preview-dl')[seg].select('td')[-1].get_text()
						project_describe = ''

					if project_content.find(u'责任描述') >0 and project_content.find(u'项目描述') >0:
						duty_describe = project_soup.select('.resume-preview-dl')[seg].select('td')[-3].get_text()
						project_describe = project_soup.select('.resume-preview-dl')[seg].select('td')[-1].get_text()

					if project_content.find(u'责任描述') <0 and project_content.find(u'项目描述') >0:
						duty_describe = ''
						project_describe = project_soup.select('.resume-preview-dl')[seg].select('td')[-1].get_text()
					seg += 1
					project_dict['project_time'] = project_time
					project_dict['project_name'] = project_name
					project_dict['duty_describe'] = duty_describe
					project_dict['project_describe'] = project_describe
					project.append(project_dict)
				self.extract['project'] = project

				'''抽取工作经历'''
			work_experience = []
			if  html.find('workExperience') >0:
				seg = 0
				for x in soup.select('.workExperience')[0].select('h2'):
					work_dict = {'work_time':'','company_name':'','working_hours':'','job_name':'','work_salary':'','company_size':'','company_type':''}
					job_name = ''
					company_size = ''
					department = ''
					work_salary = ''
					industry_belongs = ''
					company_type = ''
					manage_experience = ''
					work_common = soup.select('.workExperience')[0].select('h2')[seg].get_text().split()
					work_time = work_common[0] + work_common[1] + work_common[2]
					company_name = work_common[3]
					working_hours = work_common[-1].strip(u'（').rstrip(u'）')
					work_industry = soup.select('.workExperience')[0].select('h5')[seg].get_text().split('|')
					# if soup.select('.workExperience')[0].select('h5')[seg].get_text().find('|') >0:   # 这里的数目是不定的,暂时判断三种情况
					if len(work_industry) == 3:
						department = work_industry[0]
						job_name = work_industry[1]
						work_salary = work_industry[2]
					elif len(work_industry) == 2:
						if work_industry[0].find(u'部') >0:
							department = work_industry[0]
							job_name = ''
							work_salary = work_industry[1]
						else:
							department = ''
							job_name = work_industry[0]
							work_salary = work_industry[1]
					else:
						if work_industry[0].find(u'部') >0:
							job_name = ''
							work_salary = ''
							department = work_industry[0]
						elif work_industry[0].find('0') >0:
							job_name = ''
							work_salary = work_industry[0]
							department = ''
						else :
							job_name =work_industry[0]
							work_salary = ''
							department = ''
					work_collect = soup.select('.workExperience')[0].select('.resume-preview-dl')[seg*2]
					if len(work_collect.get_text().split('|')) == 3:
						industry_belongs = work_collect.get_text().split('|')[0].strip()
						company_type = work_collect.get_text().split('|')[1].strip().replace(u'企业性质：','')
						company_size = work_collect.get_text().split('|')[2].replace(u'规模：', '').strip()
					elif len(work_collect.get_text().split('|')) == 1:
						industry_belongs = work_collect.get_text().split('|')[0].strip()
						company_type = ''
						company_size = ''
					job_collect = soup.select('.workExperience')[0].select('.resume-preview-dl')[seg*2+1]
					job_describe = job_collect.select('tr')[0].get_text().replace(u'工作描述：','').strip()
					# if job_collect.select('tr')[1].get_text().find(u'管理经验') >0:
					# 	manage_experience = job_collect.select('tr')[1].get_text
					# 	work_dict['manage_experience'] = manage_experience
					seg += 1
					work_dict['work_time'] = work_time
					work_dict['company_name'] = company_name
					work_dict['working_hours'] = working_hours
					work_dict['company_size'] = company_size
					work_dict['job_name'] = job_name
					work_dict['department'] = department
					work_dict['work_salary'] = work_salary
					work_dict['industry_belongs'] = industry_belongs
					work_dict['company_type'] = company_type
					work_dict['job_describe'] =job_describe
					# work_dict['manage_experience'] = manage_experience
					work_experience.append(work_dict)

				self.extract['work_experience'] = work_experience

				'''抽取教育信息'''
			education = []
			# self.extract['degree'] ='bsssss'
			if html.find('educationContent') >0:
				circle_count = len(soup.select('.educationContent')[0].get_text().strip().split('\n'))
				seg = 0
				for x in range(0, circle_count):
					education_dict = {'education_time': '', 'school': '', 'major': '', 'degree': ''}
					education_common = soup.select('.educationContent')[0].get_text().strip().split('\n')[seg].split()
					education_time = education_common[0] + education_common[1] + education_common[2]
					school = education_common[3]
					if school[0] in string.lowercase:
						school = education_common[3:-2]
						school = ' '.join(school)
					major = education_common[-2]
					degree = education_common[-1]
					if len(education_common) < 5:
						school = ''
						major = ''
					if not self.extract['degree']:
						self.extract['degree'] = degree
					seg += 1
					education_dict['education_time'] = education_time
					education_dict['school'] = school
					education_dict['major'] = major
					education_dict['degree'] = degree
					graduate_time = soup.select('.educationContent')[0].get_text().strip().split('\n')[0].split()[2]
					education.append(education_dict)
					if len(education_common) > 6:
						error_path = os.path.join('/data/fetch_git/fetch/src/fetch/error/zhilian/', 'edu_'+str(time.time())+'.html')
						with open(error_path, 'w+') as f:
							f.write(html)
				school = education[0]['school']
				major = education[0]['major']

				self.extract['school'] = school
				self.extract['major']  = major
				self.extract['graduate_time'] = graduate_time
				self.extract['education'] = education

				'''抽取证书'''
			certificate = []
			if html.find('<h3 class="fc6699cc">证书</h3>') > 0:
				for m in soup.select('.resume-preview-all'):
					if m.select('h3')[0].get_text().find(u'书') >0:
						certificate_common = m
				for x in certificate_common.select('h2'):
					certificate_dict = {'certificate_time': '', 'certificate_name': ''}
					certificate_time = re.search(u'.*[$\d]',x.get_text()).group()
					certificate_name = x.get_text().replace(certificate_time, '')
					certificate_dict['certificate_time'] = certificate_time
					certificate_dict['certificate_name'] = certificate_name
					certificate.append(certificate_dict)
				self.extract['certificate'] = certificate

				'''抽取语言能力'''
			language_skill = []
			if html.find('<h3 class="fc6699cc">语言能力</h3>') > 0:
				for v in soup.select('.resume-preview-all'):
					if v.get_text().find(u'语言能力') > 0:
						language_common = v
				# circle_count = language_common.get_text().replace(u'语言能力', '').count('|')
				language_common = language_common.find_next().find_next().get_text().strip().split('\n')
				circle_count = len(language_common)
				for x in range(0, circle_count):
					language_dict = {'language': '', 'listening_speaking': '', 'reading_writing': ''}
					if language_common[x].find('|') >0:
						language = language_common[x].split(u'：')[0]
						reading_writing = language_common[x].split(u'：')[1].split('|')[0].replace(u'读写能力', '')
						listening_speaking = language_common[x].split(u'：')[1].split('|')[1].replace(u'听说能力', '')
					else:
						language = language_common[x].split(u'：')[0]
						reading_writing = ''
						listening_speaking = ''
					language_dict['language'] = language
					language_dict['reading_writing'] = reading_writing
					language_dict['listening_speaking'] = listening_speaking
					language_skill.append(language_dict)
				self.extract['language_skill'] = language_skill


			'''抽取培训经历'''
			train = []
			if html.find('<h3 class="fc6699cc">培训经历</h3>') >0:
				for l in soup.select('.resume-preview-all'):
					if l.get_text().find(u'培训经历') >0:
						train_soup = l
				seg = 0
				for x in train_soup.select('h2'):
					train_dict = {'training_time': '','training_agency': '','training_course':'','training_certificate': '','training_describe':''}
					train_common = x.get_text().split()
					training_certificate = ''
					training_describe = ''
					training_time = train_common[0] + train_common[1] + train_common[2]
					training_course =train_common[3]
					agency_num = soup.select('.resume-line-height')[seg].get_text().strip().find(u'所获证书')-soup.select('.resume-line-height')[seg].get_text().strip().find(u'培训机构')
					certificate_num = soup.select('.resume-line-height')[seg].get_text().strip().find(u'所获证书')
					training_agency = soup.select('.resume-line-height')[seg].get_text().strip()[5:certificate_num].strip()
					for i in soup.select('.resume-line-height')[0].select('td'):
						if i.get_text() == u'所获证书：':
							training_certificate = i.find_next().get_text()
					if soup.select('.resume-line-height')[0].get_text().find(u'培训描述') >0 :
						describe_num = soup.select('.resume-line-height')[0].get_text().strip().find(u'培训描述')
						training_describe = soup.select('.resume-line-height')[seg].get_text().strip()[describe_num+5:].strip()
					seg += 1
					train_dict['training_time'] = training_time
					train_dict['training_course'] = training_course
					train_dict['training_agency'] = training_agency
					train_dict['training_certificate'] = training_certificate
					train_dict['training_describe'] = training_describe
					train.append(train_dict)
				self.extract['train'] = train


			'''抽取技能'''
			skill = []
			if html.find('专业技能') >0:
				for n in soup.select('.resume-preview-all'):
					if n.get_text().find(u'专业技能') > 0:
						skill_soup = n
				circle_count = skill_soup.get_text().replace(u'专业技能', '').count('|')
				for x in range(0, circle_count):
					try:
						skill_dict = {'skill_substance': '', 'skill_level': '', 'skill_time': ''}
						skill_substance = skill_soup.get_text().replace(u'专业技能', '').strip().split('\n')[x].split(u'：')[0]
						skill_level = skill_soup.get_text().replace(u'专业技能', '').strip().split('\n')[x].split(u'：')[1].split('|')[0]
						skill_time = skill_soup.get_text().replace(u'专业技能', '').strip().split('\n')[x].split(u'：')[1].split('|')[1]
						skill_dict['skill_substance'] = skill_substance
						skill_dict['skill_level'] = skill_level
						skill_dict['skill_time'] = skill_time
						skill.append(skill_dict)
					except:
						pass
				self.extract['skill'] = skill
			return self.extract

			# json_format = json.dumps(self.extract)
			# f = open('1223.json','w+')
			# f.write(json_format)
			# f.close()
		except Exception,e:
			print traceback.format_exc()
			print Exception,e
# if __name__ =='__main__':
# 	resume_file = sys.argv[1]
# 	app = zhilian_parse(resume_file)
# 	app.run_parse()