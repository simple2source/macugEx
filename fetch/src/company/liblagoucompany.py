# coding:utf-8

import json
import requests ,re, os, codecs
from bs4 import  BeautifulSoup
from common import *
import sys, datetime
reload(sys)
sys.setdefaultencoding('utf8')

headers = {
            #'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Host': 'www.lagou.com',
            #   'Origin': 'http://www.lagou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
            # 'cookie':'JSESSIONID=8BEC55320D322A74DB30071981B109DF; LGMOID=20151216163857-12362C772F0170AAD180EA0A00F2DFD8; _ga=GA1.2.1486370829.1450157373; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1450155711,1450155904,1450157302,1450157373; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1450156287; user_trace_token=20151216163858-72e04af3-a3d0-11e5-866a-525400f775ce; LGSID=20151216163858-72e04c20-a3d0-11e5-866a-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2F; LGRID=20151217152052-b45bdb90-a48e-11e5-86b3-525400f775ce; LGUID=20151216163858-72e04e94-a3d0-11e5-866a-525400f775ce; index_location_city=%E5%B9%BF%E5%B7%9E; SEARCH_ID=f3ff410b351942edbcb9b0ee69252029; HISTORY_POSITION=1184152%2C10k-20k%2C%E5%94%AF%E5%93%81%E4%BC%9A%2CPHP%E5%B7%A5%E7%A8%8B%E5%B8%88%7C'
}

payload = {
    'first': 'false',
    'pn': 1,
    'kd': 'php'
}
keyword_list = ['PHP', 'C++', 'JS', 'javascript', 'HTML5', '安卓', 'android',
        'ios', 'java', '设计', '产品', '职能', '市场',  '测试', '运维', 'Erlang',
        'cocos2dx', '.Net', '数据分析', 'u3d', 'python']
keyword_list = ['']
city_list = ['广州', '深圳', '北京', '上海']
# s = requests.session()


def get_job_list(city='广州', keyword='php'):
    s = requests.session()
    payload['kd'] = keyword
    url = "http://www.lagou.com/jobs/positionAjax.json?px=default&city={}".format(city)
    r = post_request(url, data=payload, headers=headers)
    json_all = r.json()
    job_content = json_all['content']
    total_page_count = job_content['totalPageCount']
    # print total_page_count
    json_list = [json_all]
    if total_page_count >= 2:
        for i in xrange(2, (total_page_count+1)):
            payload['pn'] = i
            r_else = s.post(url, data=payload, headers=headers)
            json_else = r_else.json()
            json_list.append(json_else)
            rand_sleep(1)
    # print len(json_list), 99999999999999122222222222222222
    return json_list


def json_parse(json_list):
    job_list = []
    for i_json in json_list:

        #print i_json
        job_content = i_json['content']
        job_result = job_content['result']
        for i in job_result:
            job_name = i['positionName']
            job_id = i['positionId']
            company_name = i['companyShortName']
            salary = i['salary']
            resume_date = i['createTime']
            positionType = i['positionType']
            positionFirstType = i['positionFirstType']
            job_dict = {'job_id': job_id, 'job_name': job_name, 'company_name': company_name,
                        'salary': salary, 'resume_date': resume_date, 'positionFirstType': positionFirstType,
                        'positionType': positionType}
            job_list.append(job_dict)
    print len(job_list), 9999999999999
    return job_list


def get_company(job_url):

    s = requests.session()
    print job_url
    company_page = get_request(job_url, headers=headers)
    with open('lagou.html', 'w+') as f:
        f.write(company_page.text)
    # print company_page.text
    print company_page.encoding
    return company_page.text, job_url


def extract(text):
    soup = BeautifulSoup(text, 'html5lib')
    soup2 = soup.find('ul', {'class': 'c_feature'})
    soup3 = soup.find('dd', {'class': 'job_bt'})
    company_info = soup.find('dl', {'class': 'job_company'})
    company_url = get_url(soup2.a['title'])
    if not company_url:
        company_url = get_url(soup3.get_text())
    if not company_url:
        company_url = ''
    try:
        company_address = company_info.find('div', {'id': 'smallmap'}).find_previous().get_text()
    except:
        company_address = ''
    # print soup3.get_text()
    email = get_email(soup3.get_text())
    phone = get_phone(soup3.get_text())
    if email:
        email = email
    else:
        email = ''
    if phone:
        phone = phone
    else:
        phone = ''
    # print company_address, company_url, email, phone
    return company_address, company_url, email, phone

def id_company(url): # return lgid to company_id
    print '----------------'
    db2 = MySQLdb.connect(**sql_config)
    sql_sl = """ select `id` from `company_v2` where lg_company_id = '{}' limit 1""".format(url)
    print sql_sl
    cursor3 = db2.cursor()
    cursor3.execute(sql_sl)
    data = cursor3.fetchall()
    print url, data, 'company id lgtocom '
    return data[0][0]

def id_page(url): # return companyid topage_id
    print '------------'
    db2 = MySQLdb.connect(**sql_config)
    sql_sl = """ select `id` from `company_page` where company_id = '{}' limit 1""".format(url)
    print sql_sl
    cursor3 = db2.cursor()
    cursor3.execute(sql_sl)
    data = cursor3.fetchall()
    print url, data, 'page id comtopage '
    return int(data[0][0])

def do_sql(l):
    db2 = MySQLdb.connect(**sql_config)
    cursor2 = db2.cursor()
    lg_job_id,name,position_detail,salary_min,salary_max,desc,category_small,position_city,work_year,degree,lg_company_id = l
    # print pub_time
    try:
        s_company_id = id_company(lg_company_id)
        print s_company_id, 's_compnay_id'
    except:
        s_company_id = 0
    try:
        company_page_id = id_page(s_company_id)
        print company_page_id, 'company_page_id'
    except:
        company_page_id = 0
    add_time = datetime.datetime.now()
    try:
        salary_max = int(salary_max) * 12
        salary_min = int(salary_min) * 12
    except:
        pass
    sql_in = """ insert into `jobs` (lg_job_id,user_id,duty_id,recommend_id,company_id,companypage_id, `name`,
    category_small,degree,work_year,`desc`,salary_min,salary_max,
    position_city,position_detail,add_time,update_time)VALUES ('{}','{}','{}','{}','{}',
    '{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}', '{}', '{}')""".format(lg_job_id, 0, 0, 0, s_company_id,
                                                                                  company_page_id,
                                                                                  name, name, degree, work_year, desc,
                                                                                  salary_min,
                                                                                  salary_max, position_city,
                                                                                  position_detail, add_time, add_time)

    sql_up = """ update `jobs` set `name`='{}',degree='{}',work_year='{}',
`desc`='{}', `salary_min`='{}', `salary_max`='{}', `position_city`='{}',position_detail='{}',
update_time='{}' WHERE lg_job_id='{}'""".format(name,degree,work_year,desc,salary_min,salary_max,position_city,
                                                        position_detail,add_time,lg_job_id)
    print sql_in
    if not sql_selectjobs(lg_job_id):
        try:
            # print company_id
            print sql_in
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


def extract2(text):
    soup = BeautifulSoup(text, 'html.parser')
    soup2 = soup.find('ul', {'class': 'c_feature'})
    soup3 = soup.find('dd', {'class': 'job_bt'})
    company_info = soup.find('dl', {'class': 'job_company'})
    company_inurl = company_info.dt.a.get('href')
    p = re.compile('\d+')
    aa = re.search(p, company_inurl)
    if aa:
        company_id = aa.group()
    else:
        company_id = ''
    # print company_inurl
    job_type = ''  # 拉勾没有
    job_name = soup.find('dt', {'class': 'clearfix join_tc_icon'}).h1.get('title')
    company_name = soup.find('h2', {'class': 'fl'})
    company_name.span.extract()
    company_name = company_name.get_text().strip()
    company_url = get_url(soup2.a['title'])
    job_de = soup.find('dd', {'class': 'job_request'}).p
    job_del = job_de.find_all('span')
    salary = job_del[0].get_text()
    job_area = job_del[1].get_text()
    job_year = job_del[2].get_text()
    job_degree = job_del[3].get_text()
    if not company_url:
        company_url = get_url(soup3.get_text())
    if not company_url:
        company_url = ''
    try:
        company_address = company_info.find('div', {'id': 'smallmap'}).find_previous().get_text()
    except:
        company_address = ''
    # print soup3.get_text()
    job_date = soup.find('p', {'class': 'publish_time'}).get_text().split(' ')[0]
    print job_date.encode('utf8'), 99999999999999
    if job_date.find(':') > 0:
        job_date = datetime.date.today().isoformat()
    job_des = soup3.get_text()
    email = get_email(job_des)
    phone = get_phone(job_des)
    if email:
        email = email
    else:
        email = ''
    if phone:
        phone = phone
    else:
        phone = ''
    try:
        job_l = re.findall(r'\d+', salary)
        job_low = str(job_l[0]) + '000'
        job_high = str(job_l[1]) + '000'
    except:
        job_low = ''
        job_high = ''
    job_dict = {'job_name':job_name, 'job_addr': company_address, 'job_low': job_low, 'job_high': job_high,
                'job_des': job_des, 'job_type': job_type, 'job_area': job_area, 'company_id': company_id,
                'job_year': job_year, 'job_degree': job_degree, 'email': email, 'phone': phone, 'job_date': job_date,
                'company_inurl': company_inurl, 'company_url': company_url, 'job_company': company_name}
    # print job_dict
    # return job_name, update_date, company_name, salary, company_url, company_address, email, phone
    return job_dict


def run_work(city='广州', keyword='python'):

    json_list = get_job_list(city, keyword)
    job_list = json_parse(json_list)
    for job_dict in job_list:
        # print job_dict, 111111111111111
        job_id = job_dict['job_id']
        # print job_id

        keyword = convert_keyword(keyword)
        json_fname = str(keyword) + '.json'
        csv_fname = keyword + str('.csv')
        cwd_abs = os.path.abspath(__file__)
        cwd = os.path.dirname(cwd_abs)
        #store_path = os.path.join(cwd,keyword,fname)
        keyword_path = os.path.join(cwd, 'db', 'lagou', keyword)
        csv_sp = os.path.join(cwd, 'csv', 'lagou')
        csv_path = os.path.join(csv_sp, csv_fname)
        if not os.path.exists(keyword_path):
            os.makedirs(keyword_path)
        if not os.path.exists(csv_sp):
            os.makedirs(csv_sp)

        job_url = 'http://www.lagou.com/jobs/' + str(job_id) + '.html'
        # fname = str(job_id) + str('.html')
        # store_path = os.path.join(keyword_path, fname)
        job_id = str(job_id).rjust(9, '0')
        store_path = os.path.join(keyword_path,job_id[0:3], job_id[3:6], job_id +'.html')

        father_dir=os.path.dirname(store_path)
        if not os.path.exists(father_dir):
            os.makedirs(father_dir)
        #print r.text
        if not os.path.isfile(store_path):
            rand_sleep(1)
            get_company_content = get_company(job_url)
            company_page = get_company_content[0]
            not_exist = company_page.find('该信息已经被删除鸟')
            if not_exist < 0:
                # print company_page
                ex = extract(company_page)
                company_address, company_url, email, phone = ex
                job_name = job_dict['job_name']
                resume_date = job_dict['resume_date']
                company_name = job_dict['company_name']
                salary = job_dict['salary']
                job_url = get_company_content[1]
                aa = job_name, resume_date, company_name, salary, company_url, company_address, email, phone, job_url
                aa = map(lambda x:x.replace(',',''), aa)
                # print aa
                print('ID not exist, saving')
                with open(store_path, 'w') as f:
                    f.write(company_page)
                #     aa_json = json.dumps(json_dict)
                #     f.write(aa_json)
                with open(csv_path, 'a+') as f:
                    line = (','.join(aa)) + '\n'
                    line = line.replace(u'\u2022', '') # .replace(u'\xa0', '')
                    #print type(line)
                    f.write(line.encode("gbk", 'ignore'))
        sort_file(csv_path)

def run_work2(city='广州', keyword='python'):
    """ 只从岗位信息页面解析内容，插入sqlite"""
    json_list = get_job_list(city, keyword)
    job_list = json_parse(json_list)
    for job_dict in job_list:
        # print job_dict, 111111111111111
        job_id = job_dict['job_id']
        # print job_id
        job_url = 'http://www.lagou.com/jobs/' + str(job_id) + '.html'
        print job_url
        if not sql_select('lagou', job_id):
            r = get_request(job_url)
            not_exist = r.text.find('该信息已经被删除鸟')
            if not_exist < 0:
                r.encoding = 'utf-8'
                job_dict = extract2(r.text)
                sql_main('lagou', job_dict, job_url, job_id)

def sql_selectjobs( job_id=''):
    """找出table source 中是否已经存在有 url，有就不更新，对于爬所有职位而言"""
    sql = """select id from jobs WHERE lg_job_id ='{}' limit 1 """.format(job_id)
    # db = sqlite3.connect('test.db')
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    db.commit()
    cursor.execute(sql)
    data = cursor.fetchall()
    da = cursor.rowcount
    db.close()
    if len(data) > 0:
        return True
    else:
        return False


def run_work3(city='广州', keyword=''):
    """更新到jobs表"""
    json_list = get_job_list(city, keyword)
    job_list = json_parse(json_list)
    for job_dict in job_list:
        # print job_dict, 111111111111111
        job_id = job_dict['job_id']
        # print job_id
        job_url = 'http://www.lagou.com/jobs/' + str(job_id) + '.html'
        print job_url
        if not sql_selectjobs(job_id):
            r = get_request(job_url)
            not_exist = r.text.find('该信息已经被删除鸟')
            if not_exist < 0:
                r.encoding = 'utf-8'
                job_dict = extract2(r.text)
                # lg_job_id, name, position_detail, salary_min, salary_max, desc, category_small, position_city, work_year, degree, lg_company_id = l
                l = job_id, job_dict['job_name'], job_dict['job_addr'], job_dict['job_low'], job_dict['job_high'], \
                    job_dict['job_des'], job_dict['job_type'], job_dict['job_area'], job_dict['job_year'], \
                    job_dict['job_degree'], job_dict['company_id']
                do_sql(l)


if __name__ == '__main__':
    # run_work()
    for keyword in keyword_list:
        for city in city_list:
            run_work3(city, keyword)
            print city, 'done'
        print keyword, 'done'
