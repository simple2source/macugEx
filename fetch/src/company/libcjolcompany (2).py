# coding: utf-8

import requests ,re, os, codecs
from bs4 import  BeautifulSoup
from common import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')

keyword_list = ['python', 'PHP', 'C++', 'JS', 'javascript', 'HTML5', '安卓', 'android',
        'ios', 'java', '设计', '产品', '职能', '市场',  '测试', '运维', 'Erlang',
        'cocos2dx', '.Net', '数据分析', 'u3d', 'python']


params = {
    'KeywordType': 1,
    'KeyWord': '产品经理',
    'Function': '0101,0102,0103,0104,0105,0106',
    'Location': '30,2010,2008,31',
    'SearchType': 3,
    'ListType': 2,
    'page': 1,

}


json_url = 'http://s.cjol.com/service/joblistjson.aspx'

def get_job():
    params['page'] = 1
    r = get_request(json_url, params=params)
    r_json = r.json()
    job_html = r_json['JobListHtml']
    job_list = []
    while len(job_html) != 0:
        soup = BeautifulSoup(job_html, 'html.parser')
        job_content = soup.find_all('ul', {'class':"results_list_box"})
        for job_con in job_content:
            job_url = job_con.find('li', {'class': 'list_type_first'}).h3.a.get('href')
            job_name = job_con.find('li', {'class': 'list_type_first'}).h3.get_text().replace(',', ' ')
            job_salary = job_con.find('li', {'class': 'list_type_seventh'}).get_text()
            resume_date = job_con.find('li', {'class': 'list_type_eighth'}).get_text()
            company_name = job_con.find('li', {'class': 'list_type_second'}).a.get_text()
            job_id = job_con.find('li', {'class': 'list_type_checkbox'}).find('input').get('value')
            job_dict = {'job_url': job_url, 'job_name': job_name, 'salary': job_salary,
                        'resume_date': resume_date, 'company_name': company_name, 'job_id': job_id}
            # print job_url, job_name, job_salary, resume_date, company_name, job_id
            # print job_dict
            job_list.append(job_dict)
        params['page'] += 1
        r = get_request(json_url, params=params)
        r_json = r.json()
        job_html = r_json['JobListHtml']
    print len(job_list)
    return job_list

#html = get_request('http://www.cjol.com/jobs/job-7108877').text
def extract(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup2 = soup.find('div', {'class': 'company_detailedinfo company_detailedinfo_right'})
    if soup2:
        try:
            company_url = soup2.find('li', {'class': 'company_companylink'}).a.get('href')
        except:
            company_url = None
        soup3 = soup2.find_all('li')
        company_address = None
        for i in soup3:
            if i.get_text().find(u'地址：') == 0:
                company_address = i.get_text()[3:i.get_text().find(u'[地图]')].strip()
        if not company_address:
            company_address = ''
        job_in = soup.find('div', {'class': 'positionstatement clearfix'}).get_text()
        if not company_url:
            company_url = get_url(job_in)
        if not company_url:
            company_url = ''
        phone = get_phone(job_in)
        if not phone:
            phone = ''
        email = get_email(job_in)
        if not email:
            email = ''
        print company_url, company_address, email, phone
    else:
        company_address = ''
        company_url = ''
        email = ''
        phone = ''
    return company_url, company_address, email, phone

def extract2(html):
    """此函数完整解析网页"""
    soup = BeautifulSoup(html, 'html.parser')
    soup2 = soup.find('div', {'class': 'company_detailedinfo company_detailedinfo_right'})
    if soup2:
        try:
            company_url = soup2.find('li', {'class': 'company_companylink'}).a.get('href')
        except:
            company_url = None
        soup3 = soup2.find_all('li')
        company_address = None
        for i in soup3:
            if i.get_text().find(u'地址：') == 0:
                company_address = i.get_text()[3:i.get_text().find(u'[地图]')].strip()
        if not company_address:
            company_address = ''
        job_in = soup.find('div', {'class': 'positionstatement clearfix'}).get_text()
        if not company_url:
            company_url = get_url(job_in)
        if not company_url:
            company_url = ''
        phone = get_phone(job_in)
        if not phone:
            phone = ''
        email = get_email(job_in)
        if not email:
            email = ''
        print company_url, company_address, email, phone
        job_name = soup.find('h1', {'class': 'job_basicinfo_jobname'}).get_text()
        company_name = soup.find('p', {'class': 'companyinfoshow_name_box'}).get_text()
        job_date = soup.find('p', {'class': 'job_basicinfo_date'}).get_text()
        job_type = soup.find('p', {'class': 'job_detailedinfo_con_tit'}).find_next().li.a.get_text()
        print job_type, job_date, company_name, job_name
        job_left = soup.find('div', {'class': 'job_detailedinfo_con job_detailedinfo_con_left'})
        li = job_left.find_all('li')
        job_area = soup.find('span', {'class': 'job_basicinfo_address'}).get('title')
        print job_area
        job_salary = ''
        job_degree = ''
        job_year = ''
        for i in li:
            i_text = i.get_text()
            # print i_text
            if i_text.find(u'月薪：') > -1:
                print i_text
                job_salary = i_text[i_text.find('：')+1:]
            if i_text.find(u'学历：') > -1:
                job_degree = i_text[i_text.find('：')+1:]
            if i_text.find(u'经验：') > -1:
                job_year = i_text[i_text.find('：')+1:]
        print job_salary, job_degree, job_year
        try:
            job_l = re.findall(r'\d+', job_salary)
            job_low = job_l[0]
            job_high = job_l[1]
        except:
            job_low = ''
            job_high = ''
        job_des = soup.find('div', {'class': 'positionstatement clearfix'}).get_text()
        company_inurl = soup.find('p', {'class': 'companyinfoshow_name_box'}).a.get('href')
        company_inurl = 'www.cjol.com/jobs/' + company_inurl
        company_id = re.search('-\d+', company_inurl)
        if company_id:
            company_id = company_id.group()[1:]
        else:
            company_id = ''

    else:
        company_address = ''
        email = ''
        phone = ''
        job_name = ''
        job_low = ''
        job_high = ''
        job_des = ''
        job_type = ''
        job_area = ''
        job_year = ''
        job_degree = ''
        job_date = ''
        company_inurl = ''
        company_url = ''
        company_name = ''
        company_id = ''

    job_dict = {'job_name':job_name, 'job_addr': company_address, 'job_low': job_low, 'job_high': job_high,
                'job_des': job_des, 'job_type': job_type, 'job_area': job_area, 'company_id': company_id,
                'job_year': job_year, 'job_degree': job_degree, 'email': email, 'phone': phone, 'job_date': job_date,
                'company_inurl': company_inurl, 'company_url': company_url, 'job_company': company_name}
    # print job_dict
    # return job_name, update_date, company_name, salary, company_url, company_address, email, phone
    return job_dict



def run_work(keyword='产品'):
    params['KeyWord'] = keyword
    job_list = get_job()
    for job_info in job_list:
        job_url = job_info['job_url']
        print job_url
        keyword = convert_keyword(keyword)
        json_fname = str(keyword) + '.json'
        csv_fname = keyword + str('.csv')
        cwd_abs = os.path.abspath(__file__)
        cwd = os.path.dirname(cwd_abs)
        #store_path = os.path.join(cwd,keyword,fname)
        keyword_path = os.path.join(cwd, 'db', 'cjol', keyword)
        csv_sp = os.path.join(cwd, 'csv', 'cjol')
        csv_path = os.path.join(csv_sp, csv_fname)
        if not os.path.exists(keyword_path):
            os.makedirs(keyword_path)
        if not os.path.exists(csv_sp):
            os.makedirs(csv_sp)

        # fname = job_info['job_id'] + '.html'
        # store_path = os.path.join(keyword_path, fname)
        job_id = str(job_info['job_id'])
        job_id = job_id.rjust(9, '0')
        store_path = os.path.join(keyword_path,job_id[0:3], job_id[3:6], job_id +'.html')
        father_dir=os.path.dirname(store_path)
        if not os.path.exists(father_dir):
            os.makedirs(father_dir)
        #print r.text

        if not os.path.isfile(store_path):
            print('ID not exist, saving')
            r3 = get_request(job_url)
            rand_sleep(1)
            company_url, company_address, email, phone = extract(r3.text)
            aa = (job_info['job_name'], job_info['resume_date'], job_info['company_name'],
                  job_info['salary']) + (company_url, company_address, email, phone,) + (job_url,)
            aa = map(lambda x:x.replace(',',''), aa)
            # print aa
            with open(store_path, 'w') as f:
                f.write(r3.text)
            #     aa_json = json.dumps(json_dict)
            #     f.write(aa_json)
            with open(csv_path, 'a+') as f:
                line = (','.join(aa)) + '\n'
                #line = line.replace(u'\u2022', '') # .replace(u'\xa0', '')
                #print type(line)
                f.write(line.encode("gbk", 'ignore'))
        sort_file(csv_path)

def run_work2(keyword='产品'):
    params['KeyWord'] = keyword
    job_list = get_job()
    for job_info in job_list:
        job_url = job_info['job_url']
        print job_url
        job_id = re.search('-[0-9]+', job_url).group()[1:]
        print job_id
        if not sql_select('cjol', job_id):
            r = get_request(job_url)
            r.encoding = 'utf-8'
            job_dict = extract2(r.text)
            sql_main('cjol', job_dict, job_url, job_id)


if __name__ == '__main__':
    for kw in keyword_list:
        print kw, 'start', '-----------'
        run_work2(kw)
        print kw, 'done', '-------------'
    # run_work()
