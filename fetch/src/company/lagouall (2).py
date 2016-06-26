# encoding: utf8
import requests
import os, datetime, re, time
from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import liblagoucompany
import common
import lgtransfer


# # 按这个入口只能翻到300页左右，需要细分条件。  2-1-1  用遍历id方式爬所有公司
# url_0 = 'http://www.lagou.com/gongsi/0-0-0.json'
# payload = {
#     'first': 'false',
#     'pn': 40,
#     'sortField': 1,
#     'havemark': 0,
# }
header = {
    'Host': 'www.lagou.com',
    # 'Origin': 'http://www.lagou.com',
    'Referer': 'http://www.lagou.com',
    # 'Referer': 'http://www.lagou.com/gongsi/0-0-0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
}
#
# # r = common.post_request(url_0, data=payload, headers=header)
# #
# # a = r.json()
# # all_num = a['totalCount']
# #
# # l = set()
# # for i in a['result']:
# #     l.add(i['companyId'])
# # print l
# # print len(l)
#
# def lagou_page(url):
#     r = common.post_request(url_0, data=payload, headers=header)
#     a = r.json()
#     l = set()
#     if a['result']:
#         for i in a['result']:
#             l.add(i['companyId'])
#     print l
#     print len(l)
#     return l
#
# # city_list = [2, 3, 214, 212, 6, 251, 79, 184, 297, 129, 197, 80, 4, 5, 167, 149, 111,
# #              128, 148, 43, 215, 84, 217, 229, 98, 87, 44, 8, 281, 7, 234, 57, 248, 230,
# #              223, 272, 70, 19, 101, 156, 81, 153, 314, 132]
# city_list = [2]
# dev_list = [1, 2, 3, 4]
# industry_list = [24, 25, 33, 27, 29, 45, 31, 28, 47]
#
# con_all = []
#
# for i1 in city_list:
#     for i2 in dev_list:
#         for i3 in industry_list:
#             aa = str(i1) + '-' + str(i2) + '-' + str(i3)
#             con_all.append(aa)
#
# print con_all
# print len(con_all)
# ll = set()
# for i in con_all:
#     url = 'http://www.lagou.com/gongsi/' + i + '.json'
#     payload['pn'] = 1
#     print i
#     while True:
#         print len(ll)
#         r = common.post_request(url, data=payload, headers=header)
#         a = r.json()
#         l = set()
#         # if a['result']:
#         try:
#             for i in a['result']:
#                 l.add(i['companyId'])
#             ll.update(l)
#             payload['pn'] += 1
#             common.rand_sleep(1)
#         except:
#             print payload['pn']
#             break
# print ll  # 找出所有的companyID
# print len(ll)

# 拉勾的公司信息分开存储

def sql_lg(source='', company_id=''):
    """找出table source 中是否已经存在有 url，有就不更新，对于爬所有职位而言"""
    sql = """select company_id from {} WHERE company_id ='{}' """.format(source, company_id)
    db = sqlite3.connect('lagou.db')
    cursor = db.cursor()
    sql_cr = ''' create table If not EXISTS {}
            (
            company_id varchar(255) PRIMARY key,
            company_name varchar(255),
            company_verify varchar(255),
            company_type varchar(255),
            company_process varchar(255),
            company_product varchar(255),
            company_city varchar(255),
            company_inurl varchar(255),
            company_size varchar(255),
            job_num varchar(255),
            job_percent varchar(255),
            job_day varchar(255),
            last_login varchar(255),
            company_leader varchar(255),
            company_url varchar(255),
            company_word varchar(255),
            job_feedback varchar(255)
            )'''.format(source)
    cursor.execute(sql_cr)
    db.commit()
    cursor.execute(sql)
    data = cursor.fetchall()
    da = cursor.rowcount
    db.close()
    if len(data) > 0:
        return True
    else:
        return False

def sql_lg_main(source='', job_dict='', url='', company_id=''):
    """找出table source 中是否已经存在有 url，有就不更新，对于爬所有职位而言"""
    db = sqlite3.connect('lagou.db')
    cursor = db.cursor()
    sql_cr = ''' create table If not EXISTS {}
            (
            company_id varchar(255) PRIMARY key,
            company_name varchar(255),
            company_verify varchar(255),
            company_type varchar(255),
            company_process varchar(255),
            company_product varchar(255),
            company_city varchar(255),
            company_inurl varchar(255),
            company_size varchar(255),
            job_num varchar(255),
            job_percent varchar(255),
            job_day varchar(255),
            last_login varchar(255),
            company_leader varchar(255),
            company_url varchar(255),
            company_word varchar(255),
            job_feedback varchar(255)
            )'''.format(source)
    cursor.execute(sql_cr)
    db.commit()
    sql_up = ''' update {} SET company_name='{}',company_verify='{}',company_type='{}',company_process='{}',
    company_product='{}',company_city='{}',company_inurl='{}',company_size='{}',job_num='{}',job_percent='{}',
    job_day='{}',last_login='{}',job_feedback='{}',company_leader='{}', company_url='{}', company_word='{}'
    where  company_id='{}'
    '''.format(source, job_dict['company_name'], job_dict['company_verify'], job_dict['company_type'], job_dict['company_process'],
               job_dict['company_product'], job_dict['company_city'], url,
               job_dict['company_size'], job_dict['job_num'], job_dict['job_percent'], job_dict['job_day'], job_dict['last_login'],
               job_dict['job_feedback'],
               job_dict['company_leader'], job_dict['company_url'], job_dict['company_word'], company_id)
    sql_in = '''insert into {} (company_name,company_verify,company_type,company_process,company_product,
    company_city,company_inurl, company_size,job_num, job_percent,
    job_day,last_login,job_feedback,company_leader,company_url,company_word,company_id)
    values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')
    '''.format(source, job_dict['company_name'], job_dict['company_verify'], job_dict['company_type'], job_dict['company_process'],
               job_dict['company_product'], job_dict['company_city'], url,
               job_dict['company_size'], job_dict['job_num'], job_dict['job_percent'], job_dict['job_day'], job_dict['last_login'],
               job_dict['job_feedback'],
               job_dict['company_leader'], job_dict['company_url'], job_dict['company_word'], company_id)
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
        print Exception, str(e), 999999999
        db.rollback()
    db.close()


def company_parse(html):
    # 解析 拉勾的公司页面
    soup = BeautifulSoup(html, 'html.parser')
    base_info = soup.find('div', {'id': 'basic_container'})
    aa = base_info.find_all('li')
    company_type, company_process, company_size, company_city, company_product, job_num = '', '', '', '', '', ''
    company_name, company_url, company_word = '', '', ''
    company_main = soup.find('a', {'class': 'hovertips'})
    try:
        company_name = company_main.get('title').strip()
    except:
        pass
    try:
        company_url = company_main.get('href')
    except:
        pass
    try:
        company_word = soup.find('div', {'class': 'company_word'}).get_text().strip()
    except:
        pass
    # print company_name, company_url, company_word
    company_leader = ''
    soup3 = soup.find_all('p', {'class': 'item_manager_name'})
    for i3 in soup3:
        company_leader += i3.span.text + ','

    for i1 in aa:
        # print i1.i.get('class')
        if 'type' in i1.i.get('class'):
            company_type = i1.span.text
        if 'process' in i1.i.get('class'):
            company_process = i1.span.text
        if 'number' in i1.i.get('class'):
            company_size = i1.span.text
        if 'address' in i1.i.get('class'):
            company_city = i1.span.text
    company_product_soup = soup.find_all('div', {'class': 'product_url'})
    for i2 in company_product_soup:
        company_product += i2.a.text.strip() + ','
    soup2 = soup.find('div', {'class': 'company_data'}).find_all('li')
    job_num, job_percent, job_day, job_feedback, last_login = '', '', '', '', ''
    try:
        job_num = soup2[0].strong.text.strip()
    except:
        pass
    try:
        job_percent = soup2[1].strong.text.strip()
    except:
        pass
    try:
        job_day = soup2[2].strong.text.strip()
    except:
        pass
    try:
        job_feedback = soup2[3].strong.text.strip()
    except:
        pass
    try:
        last_login = soup2[4].strong.text.strip()
    except:
        pass
    if soup.find('a', {'class': 'identification'}):
        company_verify = '1'
    else:
        company_verify = '0'
    # print company_type, company_process, company_size, company_city, company_product, company_verify
    # print job_num, job_percent, job_day, job_feedback, last_login
    # print company_leader, company_name, company_url, company_word
    company_dict = {'company_type': company_type, 'company_process': company_process, 'company_size': company_size,
                    'company_city': company_city, 'company_product': company_product, 'company_verify': company_verify,
                    'job_num': job_num, 'job_percent': job_percent, 'job_day': job_day, 'job_feedback': job_feedback,
                    'last_login': last_login, 'company_leader': company_leader, 'company_name': company_name,
                    'company_url': company_url, 'company_word': company_word}
    # print len(company_dict)
    return company_dict

def get_company(company_id):
    cwd_abs = os.path.abspath(__file__)
    cwd = os.path.dirname(cwd_abs)
    # for i in xrange(1, 120000):
    print company_id
    if not sql_lg('lagou', company_id):
        url = 'http://www.lagou.com/gongsi/{}.html'.format(company_id)
        print url
        r = common.get_request(url, headers=header)
        # print r.url
        if r.status_code == 200:
            print url, '------------------' * 5
            #store_path = os.path.join(cwd,keyword,fname)
            gs_fp = os.path.join(cwd, 'gongsi', 'lagou')
            if not os.path.exists(gs_fp):
                os.makedirs(gs_fp)
            # fname = str(company_id) + '.html'
            job_id = str(company_id)
            job_id = job_id.rjust(8, '0')
            store_path = os.path.join(gs_fp,job_id[0:3], job_id[3:6], job_id +'.html')
            father_dir=os.path.dirname(store_path)
            if not os.path.exists(father_dir):
                os.makedirs(father_dir)
            with open(store_path, 'w+') as f:
                f.write(r.text)
            company_dict = company_parse(r.text)
            sql_lg_main('lagou', job_dict=company_dict, url=url, company_id=company_id)
            # common.rand_sleep(1)


if __name__ == '__main__':
    for i in xrange(23000, 40000):
        get_company(i)
        url = 'http://www.lagou.com/gongsi/{}.html'.format(i)
        # lgtransfer.run_work(url)

    # with open('ll5.html') as f:
    #     ff = f.read()
    # company_parse(ff)
