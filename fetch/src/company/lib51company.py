#-*- coding:utf-8 -*-

import requests
import os, datetime, re
from bs4 import BeautifulSoup
import datetime
#import json
#import unicodecsv as csv
import codecs
import operator, sys
import chardet
import common
reload(sys)
sys.setdefaultencoding('utf8')

payload1 = {
        'fromJs':1,
        'jobarea':'030200,040000,010000,020000,00', # 北上广深 030200,040000,010000,020000,00
        'funtype': '0000',
        'industrytype': '',
        'keyword':'安卓',
        'keywordtype':0,
        'lang': 'c',
        'stype':2,
        'postchannel': '0000',
        'fromType':1,
        'confirmdate':9
}


# 计算机行业分开两次搜索，系统限制9个选项一起选
# industry_list = ['01,37,38,31,39', '32,35,02,40']
industry_list = ['01', '37', '38', '31', '39', '32', '35', '02', '40']
# keyword_list = ['python', 'PHP', 'C++', 'JS', 'javascript', 'HTML5', '安卓', 'android',
#         'ios', 'java', '设计', '产品', '职能', '市场',  '测试', '运维', 'Erlang',
#         'cocos2dx', '.Net', '数据分析', 'u3d', 'python']
keyword_list = ['']
url = 'http://search.51job.com/jobsearch/search_result.php'

cookies_dict = {
            'guide':'1', # 关闭弹框提示，不关不返回结果页面
            'collapse_expansion': '0'}

# 找到具体信息url
def find_url(html):
    url_list = []
    soup = BeautifulSoup(html,"html5lib")
    u = soup.find_all('p', {'class': 't1'})
    for ui in u:
        url_i = ui.a.get('href')
        if url_i.startswith('http://jobs'):
            url_list.append(url_i)
    #print url_list
    return  url_list
# 抓取第一页，保存
def get_first(keyword = 'android', payload = payload1):
    url_list = []
    payload['keyword'] = keyword
    r = common.get_request(url, params=payload, cookies=cookies_dict)

    # 保存当前网址
    #print r.text
    url_list = find_url(r.text)
    with open('company.html', 'w+') as f:
       f.write(r.text.encode('ISO-8859-1'))
    return r.text, url_list


#循环遍历下一页
def get_next(html):
    soup = BeautifulSoup(html,"html5lib")
    s = soup.find_all('li', {'class': 'bk'})
    try:
        next_url = s[1].find('a').get('href')
    except:
        next_url = None
    return next_url

# run


def get_url_list(keyword):
    url_list = []
    for industry in industry_list:
        payload1['industrytype'] = industry
        s = requests.Session()
        first_result = get_first(keyword, payload1)
        first_page = first_result[0]
        n = 1
        next_url = get_next(first_page)
        url_list.extend(first_result[1])
        while next_url:
            #print next_url
            n += 1
            fname = 'company'+str(n) + '.html'
            r = common.get_request(next_url, payload1)
            #r = s.get(next_url, params = payload1, cookies=cookies_dict)
            url_list2 = find_url(r.text)
            url_list.extend(url_list2)

            next_url = get_next(r.text)

    url_list = list(set(url_list))
    print len(url_list)
    return url_list



# 在 extract()返回的 content 中找网址 或者在公司介绍，职位描述中找
# soup.find('div', {'class':'tCompany_text_gsjs'})
# 职位描述
# soup.find('div', {'class':'tCompany_text'})
def get_url(content):
    url = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    if url:
        url = url.group()
    return url

def get_salary(text):
    salary = re.search(u'[\d]+-[\d]{3,}', text)
    if salary:
        salary = salary.group()
        return salary

def extract(text):
    if get_email(text):
        email = get_email(text)
    else:
        email = ''
    soup3 = BeautifulSoup(text, "html.parser")
    sa = soup3.find('div',{'class': 'tCompany_basic_job'})
    if sa:
        sas = sa.get_text()
        if get_salary(sas):
            salary = get_salary(sas)
        else:
            salary = ''
    else:
        salary = ''
    #print soup3.original_encoding
    job_name = soup3.find('li', {'class':'tCompany_job_name'}).get_text().replace('\n','')
    # 公司网址跟地址，假如有的话
    content = soup3.find_all('p', {'class':'job_company_text'})
    #if len(content) > 1:
    try:
        gs_content = soup3.find('div',{'class':'tCompany_text'}).get_text()
    except:
        gs_content = ''
    try:
        gsjs_content = soup3.find('div', {'class': 'tCompany_text_gsjs'}).get_text()
    except:
        gsjs_content = ''
    conss = gs_content + gsjs_content
    if get_phone(conss):
        phone = get_phone(conss)
    else:
        phone = ''
    cons = ''
    try:
        for con in content:
            cons += con.get_text()
    except:
        cons = ''
    url_content = get_url(cons)
    if not url_content:
        url_content = get_url(conss)
    if not url_content:
        url_content = ''
    address_content = soup3.find('i', {'class':'iconMain20 icon20-phone'})
    if address_content:
        address_content = address_content.find_next('p', {'class':'job_company_text'}).get_text()
    else:
        address_content = ''
    #print repr(address_content)
    address_content = address_content.encode('utf-8').replace(',', '').decode('utf-8')
    #print type(address_content)
    #print address_content
    soup4 = soup3.find('div',{'class':'tBorderTop_box job_page_company'})
    #找更新日期
    soup5 = soup3.find('div', {'class':'tCompany_basic_job'})
    try:
        update_time = soup5.find('dd',{'class':'text_dd'}).get_text().strip()
    except:
        update_time = ''
    try:
        company_name = soup4.h2.get_text()
    except:
        company_name = ''

    result = (job_name, update_time, company_name, salary, url_content, address_content, email, phone)
    result_x = map(lambda x:x.replace(',',''), result)
    # return job_name, update_time, company_name, salary, url_content, address_content, email, phone
    return result_x


def extract2(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        job_name = soup.find('h1').get('title')
    except:
        job_name = ''
    try:
        job_year = soup.find('em', {'class': 'i1'}).next_element
    except:
        job_year = 0
    try:
        job_degree = soup.find('em', {'class': 'i2'}).next_element
    except:
        job_degree = ''
    try:
        job_date = soup.find('em', {'class': 'i4'}).next_element
    except:
        job_date = ''
    try:
        company_inurl = soup.find('p', {'class': 'cname'}).a.get('href')
        job_company = soup.find('p', {'class': 'cname'}).a.get('title')
    except:
        company_inurl = ''
        job_company = ''
    p = re.compile('co\d+')
    aa = re.search(p, company_inurl)
    if aa:
        company_id = aa.group()
    else:
        company_id = ''
    print job_year, job_name, job_degree
    try:
        job_salary = soup.find('div', {'class': 'cn'}).strong.get_text()
        job_l = re.findall(r'\d+', job_salary)
        job_low = job_l[0]
        job_high = job_l[1]
    except:
        job_low = ''
        job_high = ''
    print job_low, job_high
    try:
        job_addr = soup.find('div', {'class': 'bmsg inbox'}).p.contents[2].strip()
    except:
        job_addr = ''
    print job_addr
    job_str = soup.find('div', {'class': 'bmsg job_msg inbox'}).contents[2]
    job_describe = job_str.get_text().split(u'职能类别：')[0]
    job_input = soup.find_all('div', {'class': 'tBorderTop_box'})
    phone = common.get_phone(job_describe)
    email = common.get_email(job_describe)
    company_info = soup.find('div', {'class': 'tmsg inbox'}).get_text()
    company_url = common.get_url(job_describe)
    if len(phone) == 0:
        phone = common.get_phone(company_info)
    if len(email) == 0:
        email = common.get_email(company_info)
    if len(company_url) == 0:
        company_url = common.get_url(company_info)
    try:
        job_type = job_str.find('p', {'class': 'fp f2'}).find_all('span', {'class': 'el'})
        job_type = ','.join([i.get_text() for i in job_type])
    except:
        job_type = ''

    job_area = soup.find('span', {'class': 'lname'}).get_text()
    print job_area
    job_dict = {'job_name':job_name, 'job_addr': job_addr, 'job_low': job_low, 'job_high': job_high,
                'job_des': job_describe, 'job_type': job_type, 'job_area': job_area, 'company_id': company_id,
                'job_year': job_year, 'job_degree': job_degree, 'email': email, 'phone': phone, 'job_date': job_date,
                'company_inurl': company_inurl, 'company_url': company_url, 'job_company': job_company}
    return job_dict


def get_email(html):
    email = re.search("[\w.]+@[\w.]+", html)
    if email:
        email = email.group()
    if email.find('51job') < 0:
        #print type(email)
        return email

def get_phone(html):
    phone = re.search('1\d{10}', html)
    if phone:
        phone = phone.group()
        return phone

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

def run_work(keyword = 'python'):
    url_list = get_url_list(keyword)
    for url_get in url_list:
        print url_get
        job_id = re.search('[0-9]+.html', url_get).group()[:-5]
        print job_id
        if not common.sql_select('job51', job_id):
            r = common.get_request(url_get)
            if r.status_code == 200:
                r.encoding = 'gb2312'
                job_dict = extract2(r.text)
                common.sql_main('job51', job_dict, url_get, job_id)

    # s = requests.Session()
    # if keyword == '安卓':
    #     keyword = 'android'
    # if keyword == 'JS':
    #     keyword = 'javascript'
    # # 中文编码问题
    # if keyword == '设计':
    #     keyword = 'sheji'
    # if keyword == '产品':
    #     keyword = 'chanpin'
    # if keyword == '职能':
    #     keyword = 'zhineng'
    # if keyword == '市场':
    #     keyword = 'shichang'
    # if keyword == '测试':
    #     keyword = 'ceshi'
    # if keyword == '运维':
    #     keyword = 'yunwei'
    # if keyword == '数据分析':
    #     keyword = 'shujufenxi'
    # json_fname = str(keyword) + '.json'
    # csv_fname = keyword + str('.csv')
    # cwd_abs = os.path.abspath(__file__)
    # cwd = os.path.dirname(cwd_abs)
    # #store_path = os.path.join(cwd,keyword,fname)
    # keyword_path = os.path.join(cwd, 'db', '51', keyword)
    # csv_sp = os.path.join(cwd, 'csv', '51')
    # csv_path = os.path.join(csv_sp, csv_fname)
    # if not os.path.exists(keyword_path):
    #     os.makedirs(keyword_path)
    # if not os.path.exists(csv_sp):
    #     os.makedirs(csv_sp)
    # for url_get in url_list:
    #     print url_get
    #     fname = re.search('[0-9]+.html', url_get).group()
    #     job_id = re.search('[0-9]+', fname).group()
    #     job_id = job_id.rjust(9, '0')
    #     store_path = os.path.join(keyword_path,job_id[0:3], job_id[3:6], job_id +'.html')
    #
    #     father_dir=os.path.dirname(store_path)
    #     if not os.path.exists(father_dir):
    #         os.makedirs(father_dir)
    #     # store_path = os.path.join(keyword_path, fname)
    #     #print r.text
    #
    #     if not os.path.isfile(store_path):
    #         #r = s.get(url_get)
    #         r = get_request(url_get)
    #         r.encoding = "gb2312"
    #         not_exist = r.text.find(u'hot-tj-title')
    #         print 1111111111111, not_exist
    #         if not_exist < 0:
    #             print 1
    #             text = r.text.replace(u'\ufeff', '')
    #             # aa = extract(text) + (url_get,)
    #             aa = extract(text)
    #             aa.append(url_get)
    #             with open(store_path, 'w') as f:
    #                 f.write(r.text.encode('gb2312', 'ignore'))
    #             #     aa_json = json.dumps(json_dict)
    #             #     f.write(aa_json)
    #             with open(csv_path, 'a+') as f:
    #                 line = (','.join(aa)) + '\n'
    #                 f.write(line.encode("gbk", 'ignore'))
    # sort_file(csv_path)
    

if __name__ == '__main__':
#    run_work('python')
    for kw in keyword_list:
        run_work(kw)
        print kw, 'done'

