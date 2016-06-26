# coding: utf-8

import requests
import re, codecs, operator
import random,time,sqlite3
import requests.packages.urllib3
import MySQLdb

sql_config = {
    'host': "localhost",
    'user': "testuser",
    'passwd': "",
    'db': 'tuike',
    'charset': 'utf8',
}

def get_request(url, headers='', params='',cookies={}):
    s = requests.Session()
    requests.packages.urllib3.disable_warnings()
    flag = 0
    count = 1
    while flag == 0:
        try:
            r = s.get(url, headers=headers, params=params, cookies=cookies, timeout=5, verify=False, allow_redirects=False)
            print r.status_code
            if r.status_code in [200, 301, 302]:
                flag = 1
                return r
            else:
                count += 1
                if count > 3:
                    return r
                flag = 0
                rand_sleep(2)
        except Exception, e:
            # print Exception, str(e)
            flag = 0
            rand_sleep(2)



def post_request(url, data='', headers=''):
    s = requests.Session()
    requests.packages.urllib3.disable_warnings()
    flag = 0
    while flag == 0:
        try:
            r = s.post(url, data=data, headers=headers, timeout=5)
            print r.status_code
            if r.status_code == 200:
                flag = 1
                return r
            else:
                flag = 0
                rand_sleep(2)
        except Exception, e:
            print Exception, str(e)
            flag = 0
            rand_sleep(2)

def get_email(html):
    email = re.search("[\w.]+@[\w.]+", html)
    if email:
        email = email.group()
        # if email.find('51job.') < 0:
        #     #print type(email)
    else:
        email = ''
    return email

def get_phone(html):
    phone = re.search('1\d{10}', html)
    if phone:
        phone = phone.group()
    else:
        phone = ''
    return phone

def get_url(content):
    url = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    if url:
        url = url.group()
    else:
        url = ''
    return url

def sort_file(fname):
    with codecs.open(fname, 'rU', encoding='gbk') as f:
        ff = f.readlines()
    pre_sort = []
    for i in ff:
        pre_sort.append(i.split(','))
    sortlist = sorted(pre_sort, key=operator.itemgetter(2), reverse=True)
    with open(fname, 'w+') as f:
        for i in sortlist:
            f.write((',').join(i).encode('gbk'))

def convert_keyword(keyword):
    if keyword == '安卓':
        keyword = 'android'
    if keyword == 'JS':
        keyword = 'javascript'
    # 中文编码问题
    if keyword == '设计':
        keyword = 'sheji'
    if keyword == '产品':
        keyword = 'chanpin'
    if keyword == '职能':
        keyword = 'zhineng'
    if keyword == '市场':
        keyword = 'shichang'
    if keyword == '测试':
        keyword = 'ceshi'
    if keyword == '运维':
        keyword = 'yunwei'
    if keyword == '数据分析':
        keyword = 'shujufenxi'
    return keyword


def rand_sleep(sec):
    if sec > 0:
        sec = sec
    else:
        sec = 3
    sleepTime = random.random() * sec
    sleepTime = float('%0.2f' % sleepTime)
    time.sleep(sleepTime)


def sql_main(source='', job_dict='', url='', job_id=''):
    """传入 source 判断插入的table， d 为字典, job_dict={}"""
    db = MySQLdb.connect(**sql_config)
    # db = sqlite3.connect('test.db')
    cursor = db.cursor()

    sql_up = ''' update jobcrawl SET job_name='{}',job_addr='{}',job_low='{}',job_high='{}',
    job_des='{}',job_type='{}',job_area='{}',job_year='{}',job_degree='{}',job_company='{}',job_date='{}',
    company_url='{}',company_inurl='{}',email='{}',phone='{}', job_url='{}', company_id='{}'
    where  job_id='{}' and source = '{}'
    '''.format(job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'],
               db.escape_string(job_dict['job_des']), job_dict['job_type'], job_dict['job_area'], job_dict['job_year'],
               job_dict['job_degree'], job_dict['job_company'], job_dict['job_date'], job_dict['company_url'],
               job_dict['company_inurl'], job_dict['email'], job_dict['phone'], url, job_dict['company_id'], job_id, source)

    sql_in = '''insert into jobcrawl (source,job_url,job_name,job_addr,job_low,job_high,job_des,job_type,job_area,job_year,
    job_degree,job_company,job_date,company_url,company_inurl,email,phone,job_id,company_id)
    values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')
    '''.format(source, url, job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'],
               db.escape_string(job_dict['job_des']), job_dict['job_type'], job_dict['job_area'], job_dict['job_year'],
               job_dict['job_degree'], job_dict['job_company'], job_dict['job_date'], job_dict['company_url'],
               job_dict['company_inurl'], job_dict['email'], job_dict['phone'],job_id, job_dict['company_id'])
    try:
        cursor.execute(sql_up)
        data = cursor.rowcount
        print data, '-----upup----------'
        if data == 0:
            cursor.execute(sql_in)
            data2 = cursor.rowcount
            print data2, '---------ininin-------'
        db.commit()
    except Exception, e:
        print sql_in
        print Exception, str(e)
        db.rollback()
    db.close()


def sql_main2(source='', job_dict='', url='', job_id=''):   # 更新jobs 表，展示
    """传入 source 判断插入的table， d 为字典, job_dict={}"""
    db = MySQLdb.connect(**sql_config)
    # db = sqlite3.connect('test.db')
    cursor = db.cursor()

    sql_up = ''' update jobcrawl SET job_name='{}',job_addr='{}',job_low='{}',job_high='{}',
    job_des='{}',job_type='{}',job_area='{}',job_year='{}',job_degree='{}',job_company='{}',job_date='{}',
    company_url='{}',company_inurl='{}',email='{}',phone='{}', job_url='{}', company_id='{}'
    where  job_id='{}' and source = '{}'
    '''.format(job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'],
               db.escape_string(job_dict['job_des']), job_dict['job_type'], job_dict['job_area'], job_dict['job_year'],
               job_dict['job_degree'], job_dict['job_company'], job_dict['job_date'], job_dict['company_url'],
               job_dict['company_inurl'], job_dict['email'], job_dict['phone'], url, job_dict['company_id'], job_id, source)

    sql_in = '''insert into jobcrawl (source,job_url,job_name,job_addr,job_low,job_high,job_des,job_type,job_area,job_year,
    job_degree,job_company,job_date,company_url,company_inurl,email,phone,job_id,company_id)
    values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')
    '''.format(source, url, job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'],
               db.escape_string(job_dict['job_des']), job_dict['job_type'], job_dict['job_area'], job_dict['job_year'],
               job_dict['job_degree'], job_dict['job_company'], job_dict['job_date'], job_dict['company_url'],
               job_dict['company_inurl'], job_dict['email'], job_dict['phone'],job_id, job_dict['company_id'])
    try:
        cursor.execute(sql_up)
        data = cursor.rowcount
        print data, '-----upup----------'
        if data == 0:
            cursor.execute(sql_in)
            data2 = cursor.rowcount
            print data2, '---------ininin-------'
        db.commit()
    except Exception, e:
        print sql_in
        print Exception, str(e)
        db.rollback()
    db.close()





def sql_select(source='', job_id=''):
    """找出table source 中是否已经存在有 url，有就不更新，对于爬所有职位而言"""
    sql = """select job_id from jobcrawl WHERE source='{}' and job_id ='{}' limit 1 """.format(source, job_id)
    # db = sqlite3.connect('test.db')
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    # sql_cr = ''' create table If not EXISTS {}
    #         (
    #         job_id varchar(255) PRIMARY key,
    #         job_name varchar(255),
    #         job_addr varchar(255),
    #         job_low varchar(255),
    #         job_high varchar(255),
    #         job_des varchar(255),
    #         job_type varchar(255),
    #         job_area varchar(255),
    #         job_year varchar(255),
    #         job_degree varchar(255),
    #         job_company varchar(255),
    #         job_date varchar(255),
    #         job_url varchar(255),
    #         company_url varchar(255),
    #         company_inurl varchar(255),
    #         company_id varchar(255),
    #         email varchar(255),
    #         phone varchar(255)
    #         )'''.format(source)
    # cursor.execute(sql_cr)
    db.commit()
    cursor.execute(sql)
    data = cursor.fetchall()
    da = cursor.rowcount
    db.close()
    if len(data) > 0:
        return True
    else:
        return False

