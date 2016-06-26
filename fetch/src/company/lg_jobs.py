# encoding: utf8

"""
抓取入库 jobs 表 liblagoucompany 有点乱"""

import json
import requests ,re, os, codecs
from bs4 import  BeautifulSoup
from common import *
import sys, datetime
reload(sys)
sys.setdefaultencoding('utf8')
import liblagoucompany
import lagouall
import common

def do_sql2(job_dict):
    db2 = MySQLdb.connect(**sql_config)
    cursor2 = db2.cursor()
    # print job_dict
    # print job_dict['job_addr']
    l = job_dict['job_id'], job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'], \
        job_dict['job_des'], job_dict['job_type'], job_dict['job_area'], job_dict['job_year'], \
        job_dict['job_degree'], job_dict['company_id'], job_dict['positionFirstType'], job_dict['positionType'], \
        job_dict['resume_date']
    lg_job_id,name,position_detail,salary_min,salary_max,desc,category_small,position_city,work_year,degree,\
    lg_company_id, first_type, job_type, resume_date = l
    # print pub_time
    try:
        s_company_id = liblagoucompany.id_company(lg_company_id)
        print s_company_id, 's_compnay_id'
    except Exception, e:
        s_company_id = 0
        print e
    if s_company_id == 0:
        c_dict = get_company(lg_company_id)
        insert_sql_company(lg_company_id, c_dict)
    s_company_id = liblagoucompany.id_company(lg_company_id)
    try:
        company_page_id = liblagoucompany.id_page(s_company_id)
        print company_page_id, 'company_page_id'
    except Exception, e:
        company_page_id = 0
        print e
    if company_page_id == 0:
        c_dict = get_company(lg_company_id)
        insert_sql_company_page(s_company_id, c_dict)
    company_page_id = liblagoucompany.id_page(s_company_id)
    timenow = datetime.datetime.now()
    try:
        salary_max = int(salary_max) * 12
        salary_min = int(salary_min) * 12
    except:
        pass
    sql_in = """ insert into `jobs` (lg_job_id,user_id,duty_id,recommend_id,company_id,companypage_id, `name`,
    category_small,degree,work_year,`desc`,salary_min,salary_max,
    position_city,position_detail,add_time,update_time,category_big)VALUES ('{}','{}','{}','{}','{}',
    '{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}', '{}', '{}','{}')""".format(
        lg_job_id, 0, 0, 0, s_company_id, company_page_id, name, job_type, degree, work_year, desc, salary_min,
        salary_max, position_city, position_detail, resume_date, timenow, first_type)

#     sql_up = """ update `jobs` set `name`='{}',degree='{}',work_year='{}',
# `desc`='{}', `salary_min`='{}', `salary_max`='{}', `position_city`='{}',position_detail='{}',
# update_time='{}' WHERE lg_job_id='{}'""".format(name,degree,work_year,desc,salary_min,salary_max,position_city,
#                                                         position_detail,add_time,lg_job_id)
    # print sql_in
    # if not sql_select(lg_job_id):
    try:
        # print company_id
        # print sql_in
        cursor2.execute(sql_in)
        db2.commit()
    except Exception, e:
        print sql_in, Exception, e
    # else:
    #     try:
    #         cursor2.execute(sql_up)
    #         db2.commit()
    #     except Exception, e:
    #         print sql_up, Exception, e

def update_jobtime(job_id):
    timenow = datetime.datetime.now()
    sql_up = """ update `jobs` set
update_time='{}' WHERE lg_job_id='{}'""".format(timenow, job_id)
    db2 = MySQLdb.connect(**sql_config)
    cursor2 = db2.cursor()
    cursor2.execute(sql_up)
    db2.commit()
    db2.close()

def get_company(company_id):
    cwd_abs = os.path.abspath(__file__)
    cwd = os.path.dirname(cwd_abs)
    # for i in xrange(1, 120000):
    url = 'http://www.lagou.com/gongsi/{}.html'.format(company_id)
    print url
    r = common.get_request(url, headers=lagouall.header)
    # print r.url
    if r.status_code == 200:
        print url, '------------------' * 5
        #store_path = os.path.join(cwd,keyword,fname)
        # gs_fp = os.path.join(cwd, 'gongsi', 'lagou')
        # if not os.path.exists(gs_fp):
        #     os.makedirs(gs_fp)
        # # fname = str(company_id) + '.html'
        # job_id = str(company_id)
        # job_id = job_id.rjust(8, '0')
        # store_path = os.path.join(gs_fp,job_id[0:3], job_id[3:6], job_id +'.html')
        # father_dir=os.path.dirname(store_path)
        # if not os.path.exists(father_dir):
        #     os.makedirs(father_dir)
        # with open(store_path, 'w+') as f:
        #     f.write(r.text)
        company_dict = lagouall.company_parse(r.text)
        return company_dict
        # common.rand_sleep(1)

def insert_sql_company(lg_company_id, company_dict):
    # l = company_dict['company_name'], company_dict['company_verify'], company_dict['company_type'], \
    #     company_dict['company_process'], company_dict['company_product'], company_dict['commpany_city'], \
    #     company_dict['company_inurl'],
    # company_name, company_verify, company_type, company_process, company_product, company_city, company_inurl, company_size, job_num, job_percent, job_day, last_login, company_leader, company_url, company_word, job_feedback = l
    company_verify, company_name, company_word, company_city, company_type, company_size, company_url, \
    company_process, logo, full_name, tags, introduce = \
    company_dict['company_verify'], company_dict['company_short_name'], company_dict['company_word'], \
    company_dict['company_city'], company_dict['company_type'], company_dict['company_size'], \
    company_dict['company_url'], company_dict['company_process'], company_dict['logo'], \
    company_dict['company_name'], company_dict['company_tag'], company_dict['company_desc']
    timenow = datetime.datetime.now()
    sql_in = """ insert into `company_v2` (lg_company_id,lg_verified,`name`,description,city,industry,
    employees_num,url,stage, lg_logo, full_name, introduce, tags, add_time) VALUES ('{}', '{}', '{}', '{}',
      '{}', '{}', '{}', '{}', '{}', '{}','{}', '{}', '{}', '{}')""".format(lg_company_id, company_verify, company_name, company_word,
                                                               company_city, company_type, company_size, company_url,
                                                               company_process, logo, full_name, introduce, tags, timenow)
    db2 = MySQLdb.connect(**sql_config)
    cursor2 = db2.cursor()
    cursor2.execute(sql_in)
    db2.commit()
    db2.close()


def insert_sql_company_page(company_id, company_dict):
    db2 = MySQLdb.connect(**sql_config)
    cursor2 = db2.cursor()
    company_verify, company_name, company_word, company_city, company_type, company_size, company_url, \
    company_process, logo, full_name, tags, introduce = \
    company_dict['company_verify'], company_dict['company_short_name'], company_dict['company_word'], \
    company_dict['company_city'], company_dict['company_type'], company_dict['company_size'], \
    company_dict['company_url'], company_dict['company_process'], company_dict['logo'], \
    company_dict['company_name'], company_dict['company_tag'], company_dict['company_desc']
    sql_in2 = """ insert into `company_page` (company_id,`name`,short_desc,`desc`,field,employees_num,weblink,
    stage,address,add_user,update_user,add_time) VALUES ('{}',
      '{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}', '{}')""".format(company_id, company_name, company_word,
                                                                              introduce,
                                                            company_type, company_size, company_url, company_process,
                                                            company_city, '0', '0', datetime.datetime.now())
    cursor2.execute(sql_in2)
    db2.commit()
    db2.close()

def run_work(city='', keyword=''):
    json_list = liblagoucompany.get_job_list(city, keyword)
    job_list = liblagoucompany.json_parse(json_list)
    for job_dict in job_list:
        # print job_dict, 111111111111111
        job_id = job_dict['job_id']
        # print job_id
        job_url = 'http://www.lagou.com/jobs/' + str(job_id) + '.html'
        print job_url
        if not liblagoucompany.sql_selectjobs(job_id):
            r = get_request(job_url)
            not_exist = r.text.find(u'该信息已经被删除鸟')
            if not_exist < 0:
                r.encoding = 'utf-8'
                job_dict2 = liblagoucompany.extract2(r.text)
                job_dict2.update(job_dict)
                # print job_dict2
                # lg_job_id, name, position_detail, salary_min, salary_max, desc, category_small, position_city, work_year, degree, lg_company_id = l
                # l = job_id, job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'], \
                #     job_dict['job_des'], job_dict['job_type'], job_dict['job_area'], job_dict['job_year'], \
                #     job_dict['job_degree'], job_dict['company_id']
                do_sql2(job_dict2)
        else:
            update_jobtime(job_id)


if __name__ == '__main__':
    for city in liblagoucompany.city_list:
        run_work(city)
        print city, 'done'
