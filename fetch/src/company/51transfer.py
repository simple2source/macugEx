#-*- coding:utf-8 -*-

import requests
import os, datetime, re
from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import lib51company
import common


def get_page(url):
    # s = requests.session()
    # r1 = s.get(url)
    r1 = common.get_request(url)
    r1.encoding = 'gb2312'
    soup = BeautifulSoup(r1.text, 'html.parser')
    job_num = soup.find('input', {'name': 'hidTotal'}).get('value')
    job_list = []
    job_1 = soup.find_all('p', {'class': 't1'})
    for i in job_1:
        job_list.append(i.a.get('href'))

    while len(job_list) < int(job_num):
        payload = {'pageno': 2, 'hidTotal': job_num}
        r2 = common.post_request(url, data=payload)
        r2.encoding = 'gb2312'
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        job_2 = soup2.find_all('p', {'class': 't1'})
        for i2 in job_2:
            job_list.append(i2.a.get('href'))
        payload['pageno'] += 1

    print job_list

    print len(job_list), job_num
    return job_list


def main(job_list, option=0):
    """会更新旧的岗位信息 option=0
    只抓取新增加的 option=1"""
    for url in job_list:
        job_id = re.search('[0-9]+.html', url).group()[:-5]
        if option == 0:
            r1 = common.get_request(url)
            r1.encoding = 'gb2312'
            job_dict = html_extract.extract_51(r1.text)
            # job_id = re.search('[0-9]+.html', url).group()[:-5]
            common.sql_main(source='job51', job_dict=job_dict, url=url, job_id=job_id)
        if option == 1:
            if not common.sql_select('job51', job_id):
                r1 = common.get_request(url)
                r1.encoding = 'gb2312'
                job_dict = lib51company.extract2(r1.text)
                # job_id = re.search('[0-9]+.html', url).group()[:-5]
                common.sql_main(source='job51', job_dict=job_dict, url=url, job_id=job_id)

if __name__ == '__main__':
    b = sys.argv
    if len(b) > 1:
        url = b[1]
    else:
        url = 'http://jobs.51job.com/all/co3827915.html'
    job_list = get_page(url)
    main(job_list, option=0)

