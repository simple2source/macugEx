# -*- coding:utf-8 -*-
from Inputzhilian import *
from Inputcjol import *
from InputSearch import *
from id_down_51 import *
from id_down_cjol import *
from id_down_zhilian import *
import logging.config, logging,traceback
from worktitle_task import fetch_worktitle_api
from functools import wraps
# from flask_sqlalchemy import SQLALchemy
import MySQLdb
import logging
import logging.config
from flask import make_response
from flask import Flask, render_template, request, url_for
import libzldown, libcjoldown, lib51down
import libpublish
import resumetransfer
import libaccount
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:hick@115.231.92.102/tuike'
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# db = SQLALchemy(app)
log_file = '/data/fetch_git/fetch/src/fetch/log/flask.log'
fmt = '%(asctime)s %(filename)s %(funcName)s %(levelname)s Line:%(lineno)s :%(message)s'
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
handlers = logging.FileHandler(log_file)
formatter = logging.Formatter(fmt)
handlers.formatter = formatter
stdout_handler = logging.StreamHandler(sys.__stdout__)
stdout_handler.level = logging.DEBUG
stdout_handler.formatter = formatter
logger.addHandler(handlers)
logger.addHandler(stdout_handler)


# 跨域包装头
def allow_cross_domain(fun):
	@wraps(fun)
	def wrapper_fun(*args, **kwargs):
		rst = make_response(fun(*args, **kwargs))
		rst.headers['Access-Control-Allow-Origin'] = '*'
		rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
		allow_headers ="Referer,Accept,Origin,User-Agent"
		rst.headers['Access-Control-Allow-Headers'] = allow_headers
		return rst
	return wrapper_fun


@app.route('/')
@allow_cross_domain
def index():
	return "HeLLO World"


@app.route('/job51/')
@allow_cross_domain
def job51():
	try:
		t0 = time.time()
		kwargs = {}
		area = request.args.get('area')
		year = request.args.get('year')
		age = request.args.get('age')
		degree = request.args.get('degree')
		keyword = request.args.get('keyword')
		keywordtype = request.args.get('keywordtype')
		page_num = request.args.get('page')
		if page_num is None:
			page_num = '1'
		industry = request.args.get('industry')
		work_func = request.args.get('work_func')
		job_area = request.args.get('job_area')
		updatetime = request.args.get('updatetime')
		sid = request.args.get('sid')
		if updatetime is None:
			updatetime = '180'
		run = TransportSearch()
		# if page_num:
		message = run.run_crawl_first(area, year, age, degree, keyword, keywordtype,
										industry, work_func, job_area, updatetime, page_num, sid)
		# else:
		# 	run.run_crawl_first(area, year, age, degree, keyword, keywordtype,
		# 									industry, work_func, job_area, updatetime, page_num)
		# 	message = run.run_crawl(area, year, age, degree, keyword, keywordtype,industry,
		# 									work_func, job_area, updatetime, page_num)
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('get 51job use time %s ======>>>>' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('get 51job error %s ------' % str(traceback.format_exc()))


@app.route('/zhilian/')
@allow_cross_domain
def zhilian():
	try:
		t0 = time.time()
		kwargs = {}
		area = request.args.get('area')
		year = request.args.get('year')
		age = request.args.get('age')
		degree = request.args.get('degree')
		keyword = request.args.get('keyword')
		page_num = request.args.get('page')
		if page_num is None:
			page_num = '1'
		industry = request.args.get('industry')
		work_func = request.args.get('work_func')
		job_area = request.args.get('job_area')
		updatetime = request.args.get('updatetime')
		sid = request.args.get('sid')
		if updatetime is None:
			updatetime = '6,9'
		run = TransportZhlian()
		message = run.crawl_zhilian(area, year, age, degree, keyword,
									industry, work_func, job_area, updatetime, page_num, sid)
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('get zhilian use time %s =======>' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('get zhilian error %s ------' % str(traceback.format_exc()))


@app.route('/buyresume/')
@allow_cross_domain
def buyresume():
	try:
		t0 = time.time()
		kwargs = {}
		source = request.args.get('source')
		id_num = request.args.get('id')
		city = request.args.get('city')
		adviser_user = request.args.get('user')
		if id_num is None or city is None:
			message = json.dumps({'error': 'id and city is required'})
		else:
			if source == '51job':
				run = lib51down.down51job(city, id_num, adviser_user)
				message = run.run_down()
			elif source == 'zhilian':
				run = libzldown.mainfetch(city, id_num, adviser_user)
				message = run.run_work()
			elif source == 'cjol':
				run = libcjoldown.mainfetch(city, id_num, adviser_user)
				message = run.run_work()
			else:
				message = json.dumps({'error': 'not supported source'})
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('buy resume use time %s =======>' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('buy resume error %s ------' % str(traceback.format_exc()))


@app.route('/mocookie/')
@allow_cross_domain
def mocookie():
	try:
		t0 = time.time()
		kwargs = {}
		source = request.args.get('source')
		option = request.args.get('option')
		city = request.args.get('city')
		cookie_str = request.args.get('cookie_str')
		username = request.args.get('username')
		if source not in ['51job', 'zhilian', 'cjol'] :
			message = json.dumps({'error': 'source is required'})
		else:
			# 选取合适的 cookie 文件
			position = city
			if position == 'gz':
				ppp = '广州'
			elif position == 'sz':
				ppp = '深圳'
			elif position == 'bj':
				ppp = '北京'
			elif position == 'hz':
				ppp = '杭州'
			elif position == 'sh':
				ppp = '上海'
			else:
				ppp = '%'
			ppp = '%'  #  忽略地区，插件默认带地区参数，只随机几个账户容易出问题。
			acc = libaccount.Manage(source=source, option='down', location=ppp)
			if option is None or option == 'get':
				redis_key_list = acc.uni_user()
				if len(redis_key_list) > 0:
					username1 = random.choice(redis_key_list)
					logging.info('mocookie source {} select username is {}'.format(source, username1))
					username2 = username1.split('_')[1]
					ck_str = acc.redis_ck_get(username2)
					message = {'status': 'ok', 'msg': 'get cookie success', 'username': username2, 'cookie_str': ck_str}
				else:
					message = {'status': 'error', 'msg': 'cannot find valid cookie for source {} and location {}'.format(source, city)}
			elif option == 'set' and cookie_str is not None and username is not None:
				acc.redis_ck_set(username, cookie_str)
				message = {'status': 'ok', 'msg': 'set username {} cookie success'.format(username)}
			else:
				message = {'status': 'error', 'msg': 'wrong argument'}
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('get set cookie use time %s =======>' % t1)
		return json.dumps(message)
	except Exception, e:
		print e, traceback.format_exc()
		return json.dumps({'status': 'error', 'msg': str(traceback.format_exc())})
		logger.error('buy resume error %s ------' % str(traceback.format_exc()))


@app.route('/resumetrans/')
@allow_cross_domain
def resumetrans():
	try:
		t0 = time.time()
		kwargs = {}
		source = request.args.get('source')
		username = request.args.get('username')
		password = request.args.get('password')
		captcha = request.args.get('captcha')
		if captcha is None:
			captcha = ''
		if username is None or password is None:
			message = json.dumps({'error': 'username and password is required'})
		else:
			if source in ['51job', 'zhilian', 'cjol']:
				app = resumetransfer.Trans(source, username, password, captcha)
				message = app.main()
				message = json.dumps(message)
			else:
				message = json.dumps({'error': 'not supported source'})
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('resume trans use time %s =======>' % t1 )
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('resume trans error %s -----' % str(traceback.format_exc()))
		return json.dumps({'status': 'error', 'msg': 'exception {}'.format(e)})


@app.route('/pubjob/')
@allow_cross_domain
def pubjob():
	"""必须传等于16个变量, 返回51等返回的预览网页，目前还没有发布过真实数据"""
	try:
		t0 = time.time()
		kwargs = {}
		required_arg_list = ['source', 'job_name', 'job_type', 'work_type', 'city', 'district', 'work_address',
							 'job_num', 'salary', 'work_year', 'degree', 'major', 'welfare', 'keyword', 'email',
							 'job_describe']
		for item in required_arg_list:
			if item not in request.args:
				return json.dumps({'error': 'possible missing params check your argument again must have 16 arguments'})
		source = request.args.get('source')
		job_name = request.args.get('job_name')
		job_type = request.args.get('job_type')
		work_type = request.args.get('work_type')
		city = request.args.get('city')
		district = request.args.get('district')
		work_address = request.args.get('work_address')
		job_num = request.args.get('job_num')
		salary = request.args.get('salary')
		work_year = request.args.get('work_year')
		degree = request.args.get('degree')
		major = request.args.get('major')
		welfare = request.args.get('welfare')
		keyword = request.args.get('keyword')
		email = request.args.get('email')
		job_describe = request.args.get('job_describe')
		if city == u'广州':
			location = 'gz'
		elif city == u'北京':
			location = 'bj'
		elif city == u'上海':
			location = 'sh'
		elif city == u'深圳':
			location = 'sz'
		else:
			message = json.dumps({'error': 'not support location {}'.format(city)})
			return message
		if source not in ['zhilian', '51job', 'cjol']:
			message = json.dumps({'error': 'not support source {}'.format(source)})
		# 转回字典是为了跟以前的兼容。。
		source_json = {
			'source': source,
			'job_detail': {
				'job_name': job_name, # 'lal34ala2222',  # 职位名称
				'job_type': job_type, # u'硬件测试',  # 职位类别  这个的话51 的选择太多，先不做判断
				'work_type': work_type, #  # 工作性质 全职，兼职
				'city': city, #  '广州',  # 发布城市
				'district': district, # '海珠区',  # 区
				'work_address': work_address, # '高大上',  # 上班地址
				'job_num': job_num, # '1',  # 招聘人数
				'salary': salary,  # '19320',  # 月薪，输入数字， 判断选择范围
				'work_year': work_year,  # '3',  # 工作年限，输入数字，判断选择范围
				# 可选
				'degree': degree,  # u'博士',  # 学历
				'major': major,  #  u'计算机科学与技术',  # 专业  智联不需要
				# 'publish_day': '2015-12-31',  # 发布日志，只有cjol有
				# 'department': '',  所属公司部门，意义不大
				# 'sex': '男',  # 性别  51job 没有 只有 cjol 有,  智联把区分性别当做歧视
				'welfare': welfare, # u'五险一金 222 111 高温补贴',  # 福利 以空白做分隔符
				'keyword': keyword, #'前景 高薪',  # 职位关键词，方便搜索
				'email': email, # 'a@a.com',  # 接受系统自动转发的简历
				'job_describe': job_describe, # '大家好，大家好，大家好。',  # 这是职位描述，用户自行添加
			}
		}
		json_str = json.dumps(source_json)
		if location is None or json_str is None:
			message = json.dumps({'error': 'location and json format str is required'})
		else:
			pu = libpublish.mainfetch(location, json_str)
			message = pu.run_work()
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('pub job use time %s' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('pub job error %s -----' % str(traceback.format_exc()))


@app.route('/cjol/')
@allow_cross_domain
def cjol():
	try:
		t0 = time.time()
		kwargs = {}
		area = request.args.get('area')
		year = request.args.get('year')
		age = request.args.get('age')
		degree = request.args.get('degree')
		keyword = request.args.get('keyword')
		page_num = request.args.get('page')
		if page_num is None:
			page_num = '1'
		industry = request.args.get('industry')
		work_func = request.args.get('work_func')
		job_area = request.args.get('job_area')
		updatetime = request.args.get('updatetime')
		run = TransportCjol()
		message = run.crawl_cjol(area, year, age, degree, keyword,
									industry, work_func, job_area, updatetime, page_num)
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('get cjol use time %s ======>' % t1)
		return message

	except Exception, e:
		print e, traceback.format_exc()
		logger.error('get cjol error %s -----' % str(traceback.format_exc()))


@app.route('/id51/')
@allow_cross_domain
def id51():
	try:
		t0 = time.time()
		kwargs = {}
		resume_id = request.args.get('id')
		run = TransportSearch()
		flag = run.id_down(resume_id)
		if flag == 1:
			message = {'code': flag, 'msg': 'insert success'}
		elif flag == -1:
			message = {'code': flag, 'msg': 'update success'}
		elif flag == 0:
			message = {'code': flag, 'msg': 'not insert'}
		elif flag == -2:
			message = {'code': flag, 'msg': 'parse error'}
		elif flag == -3:
			message = {'code': flag, 'msg': 'source error'}
		elif flag == -5:
			message = {'code': flag, 'msg': 'operate error'}
		elif flag == 8:
			message = {'code': flag, 'msg': 'resume secret'}
		elif flag == 9:
			message = {'code': flag, 'msg': 'resume remove'}
		elif flag == 10:
			message = {'code': flag, 'msg': 'more busy action'}
		elif flag == -10:
			message = {'code': flag, 'msg': 'already update'}
		elif flag == -11:
			message = {'code': flag, 'msg': 'id html not exist'}
		message = json.dumps(message)
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('id51 use time %s =======>' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('id51 error %s -----' % str(traceback.format_exc()))


@app.route('/idz/')
@allow_cross_domain
def idz():
	try:
		t0 = time.time()
		kwargs = {}
		resume_id = request.args.get('id')
		run_id = IdDownzhilian(resume_id)
		flag = run_id.get_id()
		if flag == 1:
			message = {'code': flag, 'msg': 'insert success'}
		elif flag == -1:
			message = {'code': flag, 'msg': 'update success'}
		elif flag == 0:
			message = {'code': flag, 'msg': 'not insert'}
		elif flag == -2:
			message = {'code': flag, 'msg': 'parse error'}
		elif flag == -3:
			message = {'code': flag, 'msg': 'source error'}
		elif flag == -5:
			message = {'code': flag, 'msg': 'operate error'}
		elif flag == 8:
			message = {'code': flag, 'msg': 'resume secret'}
		elif flag == 9:
			message = {'code': flag, 'msg': 'resume remove'}
		elif flag == 10:
			message = {'code': flag, 'msg': 'more busy action'}
		elif flag == -10:
			message = {'code': flag, 'msg': 'already update'}
		elif flag == -11:
			message = {'code': flag, 'msg': 'id html not exist'}
		message = json.dumps(message)
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('idz use time %s =======>' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('idz error %s ------' % str(traceback.format_exc()))


@app.route('/idc/')
@allow_cross_domain
def idc():
	try:
		t0 = time.time()
		kwargs = {}
		resume_id = request.args.get('id')
		run_id = IdDowncjol(resume_id)
		flag = run_id.get_id()
		if flag == 1:
			message = {'code': flag, 'msg': 'insert success'}
		elif flag == -1:
			message = {'code': flag, 'msg': 'update success'}
		elif flag == 0:
			message = {'code': flag, 'msg': 'not insert'}
		elif flag == -2:
			message = {'code': flag, 'msg': 'parse error'}
		elif flag == -3:
			message = {'code': flag, 'msg': 'source error'}
		elif flag == -5:
			message = {'code': flag, 'msg': 'operate error'}
		elif flag == 8:
			message = {'code': flag, 'msg': 'resume secret'}
		elif flag == 9:
			message = {'code': flag, 'msg': 'resume remove'}
		elif flag == 10:
			message = {'code': flag, 'msg': 'more busy action'}
		elif flag == -10:
			message = {'code': flag, 'msg': 'already update'}
		message = json.dumps(message)
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		logger.info('idc use time %s ======>' % t1)
		return message
	except Exception, e:
		print e, traceback.format_exc()
		logger.error('idc error %s ------' % str(traceback.format_exc()))


@app.route('/task/')
@allow_cross_domain
def task():
	try:
		t0 = time.time()
		form = request.args.get('form')
		fetch_task = fetch_worktitle_api.WorkTitle()
		t1 = str('%.2f' % (time.time() - t0)) + 's'
		if form == 'json':
			data = json.dumps(fetch_task.form_data())
			logger.info('get task use time %s ======>' % t1)
			return data
		else:
			data = fetch_task.form_data(flag=1)
			logger.info('get task use time %s ======>' % t1)
			return data

	except Exception, e:
		print e, traceback.format_exc()
		logger.error('task error %s ----' % str(traceback.format_exc()))


@app.route('/hierarchy/')
@app.route('/hierarchy/<name>/')
@allow_cross_domain
def hierarchy(name=None):
	if name:
		t0 = time.time()
		data_query = {
			'code': 0,
			'msg': 'OK'}
		db = connect_mysql()
		cur = db.cursor()
		if name == 'update':
			try:
				primary_id = request.args.get('primary_id')
				keyword = request.args.get('keyword')
				job_id = request.args.get('job_id')
				parent_id = request.args.get('parent_id')
				score = request.args.get('score')
				sql = """ UPDATE `hierarchy_keyword` SET keyword='{}', job_id='{}', parent_id='{}',
				score='{}' WHERE id='{}'""".format(keyword, job_id, parent_id, score, primary_id)
				res = cur.execute(sql)
				db.commit()
				db.close()
				data_query['data'] = res
				data_return = json.dumps(data_query)
				t1 = str('%.2f' % (time.time() - t0)) + 's'
				logger.info('hierarchy update use time %s' % t1)
				return data_return
			except Exception, error:
				db.rollback()
				data_query['code'] = 1
				data_query['msg'] = error
				data_return = json.dumps(data_query)
				return data_return

		elif name == 'insert':
			try:
				keyword = request.args.get('keyword')
				job_id = request.args.get('job_id')
				parent_id = request.args.get('parent_id')
				score = request.args.get('score')
				sql = """INSERT INTO `hierarchy_keyword` (keyword, job_id, parent_id, score)
				VALUES ('{}','{}','{}','{}')""".format(keyword, job_id, parent_id, score)
				res = cur.execute(sql)
				db.commit()
				db.close()
				data_query['data'] = res
				data_return = json.dumps(data_query)
				return data_return
			except Exception, error:
				db.rollback()
				data_query['code'] = 1
				data_query['msg'] = error
				data_return = json.dumps(data_query)
				return data_return

		elif name == 'del':
			try:
				primary_id = request.args.get('primary_id')
				sql = """DELETE FROM `hierarchy_keyword` WHERE id='{}'""".format(primary_id)
				res = cur.execute(sql)
				db.commit()
				db.close()
				data_query['data'] = res
				data_return = json.dumps(data_query)
				return data_return
			except Exception, error:
				db.rollback()
				data_query['code'] = 1
				data_query['msg'] = error
				data_return = json.dumps(data_query)
				return data_return

		elif name == 'query':
			page = request.args.get('page')
			if request.args.get('father'):
				try:
					father_query = request.args.get('father')
					sql_count = """SELECT count(*) FROM `hierarchy_keyword` WHERE keyword LIKE "%{}%" or
						parent_id in(SELECT DISTINCT id FROM `hierarchy_keyword` where keyword
						LIKE "%{}%")""".format(father_query, father_query)
					cur.execute(sql_count)
					count = cur.fetchall()
					if not page:
						sql = """SELECT * FROM `hierarchy_keyword` WHERE keyword LIKE "%{}%" or
						parent_id in(SELECT DISTINCT id FROM `hierarchy_keyword` where keyword
						LIKE "%{}%") ORDER BY id desc limit 20""".format(father_query, father_query)
					else:
						sql = """SELECT * FROM `hierarchy_keyword` WHERE keyword LIKE "%{}%" or
						parent_id in(SELECT DISTINCT id FROM `hierarchy_keyword` where keyword
						LIKE "%{}%") ORDER BY id desc limit {},20""".format(father_query, father_query, 20*(int(page)-1))
					res = cur.execute(sql)
					if res == 0L:
						data_query['data'] = 'empty'
						data_query['count'] = 0
						data_return = json.dumps(data_query)
						db.close()
						return data_return
					else:
						data = cur.fetchall()
						data_query['data'] = data
						data_query['count'] = count[0][0]
						data_return = json.dumps(data_query)
						db.close()
						return data_return

				except Exception, error:
					data_query['code'] = 1
					data_query['msg'] = error
					data_return = json.dumps(data_query)
					return data_return

			elif request.args.get('son'):
				try:
					son_query = request.args.get('son')
					sql_count = """SELECT count(*) FROM `hierarchy_keyword` WHERE keyword
						LIKE '%{}%'""".format(son_query)
					cur.execute(sql_count)
					count = cur.fetchall()
					if not page:
						sql = """SELECT * FROM `hierarchy_keyword` WHERE keyword
						LIKE '%{}%' ORDER BY ID DESC LIMIT 20""".format(son_query)
					else:
						sql = """SELECT * FROM `hierarchy_keyword` WHERE keyword
						LIKE '%{}%' ORDER BY ID DESC LIMIT {},20""".format(son_query, 20*(int(page)-1))
					res = cur.execute(sql)
					if res == 0L:
						data_query['data'] = 'empty'
						data_query['count'] = 0
						data_return = json.dumps(data_query)
						db.close()
						return data_return
					else:
						data = cur.fetchall()
						data_query['data'] = data
						data_query['count'] = count[0][0]
						data_return = json.dumps(data_query)
						db.close()
						return data_return
				except Exception, error:
					data_query['code'] = 1
					data_query['msg'] = error
					data_return = json.dumps(data_query)
					db.close()
					return data_return
			else:
				return hierarchy_view()
	else:
		return render_template('hierarchy.html')


@app.route('/hierarchyView')
@allow_cross_domain
def hierarchy_view():
	data_query = {
		'code': 0,
		'msg': 'OK'
	}
	db = connect_mysql()
	try:
		page = request.args.get('page')
		cur = db.cursor()
		sql_count = """SELECT count(*) FROM `hierarchy_keyword`"""
		cur.execute(sql_count)
		count = cur.fetchall()
		data_query['count'] = count[0][0]
		if not page:
			sql = """SELECT * FROM `hierarchy_keyword` ORDER BY ID DESC LIMIT 20"""
			cur.execute(sql)
			data = cur.fetchall()
			data_query['data'] = data
			db.close()
			data_return = json.dumps(data_query)
			return data_return
		else:
			sql = """SELECT * FROM `hierarchy_keyword`
				ORDER BY ID DESC LIMIT {},20""".format((int(page)-1))
			cur.execute(sql)
			data = cur.fetchall()
			data_query['data'] = data
			db.close()
			data_return = json.dumps(data_query)
			return data_return
	except Exception, error:
		data_query['code'] = 1
		data_query['msg'] = error
		data_return = json.dumps(data_query)
		db.close()
		return data_return


def connect_mysql():
	sql_config = {
		'host': "10.4.14.233",
		'user': "tuike",
		'passwd': "sv8VW6VhmxUZjTrU",
		'db': "tuike",
		'charset': "utf8",
	}
	db = MySQLdb.connect(**sql_config)
	return db


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8086)
