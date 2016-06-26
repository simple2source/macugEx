# encoding: utf8
import requests
import os, datetime, re
from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import liblagoucompany
import common


headers = {
            #'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Host': 'www.lagou.com',
            'Origin': 'http://www.lagou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
}

payload = {
    'companyId': '451',
    'positionFirstType': '全部',
    'pageNo': 1,
    'pageSize': 10,
}


def company_payload(company_url):
    """得到公司的id，修改payload"""
    p = re.compile('\d+')
    aa = re.search(p, company_url)
    company_id = aa.group()
    payload['companyId'] = company_id
    headers['Referer'] = company_url
    return payload


def get_job_list(payload):
    url = "http://www.lagou.com/gongsi/searchPosition.json"
    payload['pageNo'] = 1
    r = common.post_request(url, data=payload, headers=headers)
    json_all = r.json()
    job_content = json_all['content']['data']['page']
    total_page_count = job_content['totalCount']

    job_list = []
    for i in job_content['result']:
        job_list.append(i['positionId'])
    i = 1
    while len(job_list) < int(total_page_count):
        print 'total_page_count', total_page_count
        print 'len job list', len(job_list)
        i += 1
        print 'current page count', i
        payload['pageNo'] = i
        r_else = common.post_request(url, data=payload, headers=headers)
        json_else = r_else.json()
        job2_content = json_else['content']['data']['page']
        for i3 in job2_content['result']:
            job_list.append(i3['positionId'])
    print len(job_list)
    return job_list


def run_work(url):
    cwd_abs = os.path.abspath(__file__)
    cwd = os.path.dirname(cwd_abs)
    payload = company_payload(url)
    job_list = get_job_list(payload)
    for job_id in job_list:
        job_url = 'http://www.lagou.com/jobs/' + str(job_id) + '.html'
        print job_url
        if not common.sql_select('lagou', job_id):
            r = common.get_request(job_url)
##            if r.status_code == 200:
##                r.encoding = 'utf-8'
##                job_dict = liblagoucompany.extract2(r.text)
##                common.sql_main('lagou', job_dict, job_url, job_id)
##                gs_fp = os.path.join(cwd, 'jobs', 'lagou')
##                if not os.path.exists(gs_fp):
##                    os.makedirs(gs_fp)
##                job_id = str(job_id).rjust(9, '0')
##                store_path = os.path.join(gs_fp,job_id[0:3], job_id[3:6], job_id +'.html')
##                father_dir=os.path.dirname(store_path)
##                if not os.path.exists(father_dir):
##                    os.makedirs(father_dir)
##                with open(store_path, 'w+') as f:
##                    f.write(r.text)
##                common.rand_sleep(1)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                job_dict = liblagoucompany.extract2(r.text)
                common.sql_main('lagou', job_dict, job_url, job_id)


if __name__ == '__main__':
    # b = sys.argv
    # if len(b) > 1:
    #     url = b[1]
    # else:
    #     url = 'http://www.lagou.com/gongsi/j19727.html'
    # run_work(url)
    payload['companyId'] = '55'
    get_job_list(payload)

