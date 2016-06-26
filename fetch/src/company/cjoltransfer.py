# encoding: utf8
import requests
import os, datetime, re
from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import libcjolcompany
import common


def company_id(url):
    """get company_id from url"""
    p = re.compile('-\d+')
    aa = re.search(p, url).group()[1:]
    return aa


def job_list(c_id):
    param = {
        'CompanyID': c_id,
        'PageNo': '1',
        'PageSize': '100',
    }
    header = {
        'Host': 'www.cjol.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML'
                      ', like Gecko) Chrome/47.0.2526.111 Safari/537.36'
    }
    curl = 'http://www.cjol.com/jobs/company/joblist'
    r = common.get_request(curl, params=param, headers=header)
    job_l = []
    soup = BeautifulSoup(r.text, 'html.parser')
    soupa = soup.find_all('a')
    for a in soupa:
        job_id = company_id(a.get('href'))
        job_l.append(job_id)
    return job_l

def run_work(url):
    cid = company_id(url)
    job_l = job_list(cid)
    for job_id in job_l:
        job_url = 'http://www.cjol.com/jobs/job-' + job_id
        print job_url
        print job_id
        if not common.sql_select('cjol', job_id):
            r = common.get_request(job_url)
            r.encoding = 'utf-8'
            job_dict = libcjolcompany.extract2(r.text)
            common.sql_main('cjol', job_dict, job_url, job_id)

if __name__ == '__main__':
    b = sys.argv
    if len(b) > 1:
        url = b[1]
    else:
        url = 'http://www.cjol.com/jobs/company-73411'
    # company_id(url)
    run_work(url)
