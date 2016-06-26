# coding: utf-8

from common import *
import requests
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os

s = requests.session()

url = 'http://sou.zhaopin.com/jobs/searchresult.ashx'

headers = {
            'Host': 'sou.zhaopin.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
}

params = {
            'pd':7,  # 最近7天更新
            'jl':'广州',  # 广州+上海+北京+深圳',
            'in': '210500;160400;160000;160500;160200;300100;160100;160600',
            'kw':'php', # 关键词
            'sm':0,
            'p':1,  # 页数
            'sf':0,
            'st':99999,
            'kt':3,
            'isadv':1,
            # 'sg': '3c7ba787239d400ab2a1e407e8698a67'
          }

# 四城市一起搜，结果太多，分开
city_list = ['广州', '深圳', '北京', '上海']
# keyword_list = ['python', 'PHP', 'C++', 'JS', 'javascript', 'HTML5', '安卓', 'android',
#         'ios', 'java', '设计', '产品', '职能', '市场',  '测试', '运维', 'Erlang',
#         'cocos2dx', '.Net', '数据分析', 'u3d', 'python']
keyword_list = ['']
industry_list = ['210500', '160400', '160000', '160500', '160200', '300100', '160100', '160600']
# r = get_request(url, headers,  params)
# print r.url
#
# print r.encoding
# #print r.text
#
# with open('zl.html', 'w+') as f:
#     f.write(r.text)


def find_next(html):
    soup = BeautifulSoup(html, 'html.parser')
    next_url = soup.find('li', {'class': 'pagesDown-pos'})
    if next_url:
        next_url = next_url.a.get('href')
    return next_url

def get_url_list(html):
    soup = BeautifulSoup(html, "html.parser")
    soup2 = soup.find_all('div', {'style':"width: 224px;*width: 218px; _width:200px; float: left"})
    url_list = []
    # print type(soup2)
    # print soup2[0].a.get('href')
    for item in soup2:
     #  print item, # item.find('href') #type(item)
        url_list.append(item.a.get('href'))
    #print url_list[0], len(url_list), 4444444444444
    return url_list


def get_url_all(keyword='python', city='广州'):
    params['kw'] = keyword
    params['jl'] = city
    for industry in industry_list:
        params['in'] = industry
        r = get_request(url, headers, params)
        url_first = get_url_list(r.text)
        url_all = url_first
        flag = 1
        while flag:
            url_next = find_next(r.text)
            # print url_next, 22222222222222
            if url_next:
                url_next_list = get_url_list(r.text)
                url_all.extend(url_next_list)
                r = get_request(url_next)
            else:
                flag = 0
        # print url_all, len(url_all), 111111111111
        return url_all
        #return url_all

def extract(html):
    soup = BeautifulSoup(html, 'html.parser')
    with open('zltext.html', 'w+') as f:
        f.write(html)
    job_name = soup.find('div', {'class':'inner-left fl'})
    if job_name:
        job_name =job_name.h1.get_text()
        company_name= soup.find('div', {'class':'inner-left fl'}).h2.get_text()
        company_inurl= soup.find('div', {'class':'inner-left fl'}).h2.a.get('href')
        p = re.compile('CC\d+.htm')
        aa = re.search(p, url)
        if aa:
            company_id = aa.group()[:-4]
        else:
            company_id = ''
        job_info = soup.find('ul', {'class':'terminal-ul clearfix'})
        soup3 = job_info.find_all('strong')
        # print soup3
        # print soup3[1].get_text()
        salary = soup3[0].get_text()
        job_area = soup3[1].get_text()
        job_type = soup3[-1].get_text()
        job_year = soup3[4].get_text()
        job_degree = soup3[5].get_text()

        update_date = soup3[2].get_text()
        company_info = soup.find('div', {'class': 'company-box'}).find_all('span')
        company_address = ''
        company_url = ''
        for span in company_info:
            # print company_info
            # print repr(span), span, type(span), 333333333333333
            # print span.get_text(),222222222222
            if span.get_text() == u'公司地址：':
                # print span.find_next(), repr(span.find_next()), 909999999999
                # print span.find_next().get_text(), 444444444444444444444444
                company_address = span.find_next().get_text().strip().replace('\n', '')
            if span.get_text() == u'公司主页：':
                company_url = span.find_next().get_text().strip()
        job_describe = soup.find('div', {'class': 'tab-cont-box'}).get_text()
        email = get_email(job_describe)
        phone = get_phone(job_describe)
        if not company_url:
            company_url = get_url(job_describe)
        try:
            job_l = re.findall(r'\d+', salary)
            job_low = job_l[0]
            job_high = job_l[1]
        except:
            job_low = ''
            job_high = ''
        soup4 = soup.find('div', {'class': 'tab-inner-cont'})
        ss = str(soup4)
        s1 = ss.find('<!-- SWSStringCutStart -->')
        s2 = ss.find('<!-- SWSStringCutEnd -->')
        job_des = ss[s1+26:s2]
        job_des = BeautifulSoup(job_des, 'html.parser').get_text()
        # if company_url:
        #     company_url = company_url
        # else:
        #     company_url = ''
        # if email:
        #     email = email
        # else:
        #     email = ''
        # if phone:
        #     phone = phone
        # else:
        #     phone = ''
    else:
        job_name = ''
        update_date = ''
        company_name = ''
        salary = ''
        company_url = ''
        company_address = ''
        email = ''
        phone = ''
        job_low = ''
        job_high = ''
        job_des = ''
        job_type = ''
        job_area = ''
        job_year = ''
        job_degree = ''
        company_inurl = ''
        company_id = ''
    job_dict = {'job_name':job_name, 'job_addr': company_address, 'job_low': job_low, 'job_high': job_high,
                'job_des': job_des, 'job_type': job_type, 'job_area': job_area, 'company_id': company_id,
                'job_year': job_year, 'job_degree': job_degree, 'email': email, 'phone': phone, 'job_date': update_date,
                'company_inurl': company_inurl, 'company_url': company_url, 'job_company': company_name}

    # return job_name, update_date, company_name, salary, company_url, company_address, email, phone
    return job_dict

def run_work(keyword='python', city='广州'):
    url_all = get_url_all(keyword,city)
    for url_get in url_all:
        print url_get
        job_id = re.search('[0-9]+.htm', url_get).group()[:-5]
        print job_id
        if not sql_select('zhilian', job_id):
            r = get_request(url_get)
            r.encoding = 'utf-8'
            job_dict = extract(r.text)
            sql_main('zhilian', job_dict, url_get, job_id)

    # keyword = convert_keyword(keyword)
    # json_fname = str(keyword) + '.json'
    # csv_fname = keyword + str('.csv')
    # cwd_abs = os.path.abspath(__file__)
    # cwd = os.path.dirname(cwd_abs)
    # #store_path = os.path.join(cwd,keyword,fname)
    # keyword_path = os.path.join(cwd, 'db', 'zhilian', keyword)
    # csv_sp = os.path.join(cwd, 'csv', 'zhilian')
    # csv_path = os.path.join(csv_sp, csv_fname)
    # if not os.path.exists(keyword_path):
    #     os.makedirs(keyword_path)
    # if not os.path.exists(csv_sp):
    #     os.makedirs(csv_sp)
    #
    # for job_url in url_all:
    #     print job_url
    #     fname = re.search('[0-9]+.htm', job_url).group()
    #     # store_path = os.path.join(keyword_path, fname)
    #     #print r.text
    #     job_id = re.search('[0-9]+', fname).group()
    #     job_id = job_id.rjust(9, '0')
    #     store_path = os.path.join(keyword_path,job_id[0:3], job_id[3:6], job_id +'.html')
    #     father_dir=os.path.dirname(store_path)
    #     if not os.path.exists(father_dir):
    #         os.makedirs(father_dir)
    #
    #     if not os.path.isfile(store_path):
    #         url_text = ''
    #         while len(url_text) <= 0:
    #             url_text = get_request(job_url).text
    #             rand_sleep(4)
    #             print 'sleeping 4s'
    #         aa = extract(url_text)
    #         aa = aa + (job_url,)
    #         aa = map(lambda x:x.replace(',',''), aa)
    #         print('ID not exist, saving')
    #         with open(store_path, 'w') as f:
    #             f.write(url_text)
    #         #     aa_json = json.dumps(json_dict)
    #         #     f.write(aa_json)
    #         with open(csv_path, 'a+') as f:
    #             print aa
    #             line = (','.join(aa)) + '\n'
    #             line = line.replace(u'\u2022', "")
    #             #print type(line)
    #             f.write(line.encode("gbk", 'ignore'))
    # sort_file(csv_path)


if __name__ == '__main__':
    #run_work()
    for keyword in keyword_list:
        for city in city_list:
            run_work(keyword, city)
        print '----------------', keyword, 'done', '-------------------'




