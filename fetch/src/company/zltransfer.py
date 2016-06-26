import requests
import os, datetime, re
from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import libzlcompany
import common

headers = {
            'Host': 'sou.zhaopin.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
}


def company_link(url):
    ''' get company search_link  '''
    p = re.compile('CC\d+.htm')
    aa = re.search(p, url)
    link = aa.group()[:-4]
    link = 'http://sou.zhaopin.com/jobs/companysearch.ashx?CompID=' + link
    return link


def get_url_all(url):
    r = common.get_request(url, headers)
    url_first = libzlcompany.get_url_list(r.text)
    url_all = url_first
    flag = 1
    while flag:
        url_next = libzlcompany.find_next(r.text)
        # print url_next, 22222222222222
        if url_next:
            url_next_list = libzlcompany.get_url_list(r.text)
            url_all.extend(url_next_list)
            r = common.get_request(url_next)
        else:
            flag = 0
    # print url_all, len(url_all), 111111111111
    return url_all


def run_work(curl):
    url_all = get_url_all(curl)
    for url_get in url_all:
        print url_get
        job_id = re.search('[0-9]+.htm', url_get).group()[:-5]
        print job_id
        if not common.sql_select('zhilian', job_id):
            print common.sql_select('zhilian', job_id)
            r = common.get_request(url_get)
            r.encoding = 'utf-8'
            job_dict = libzlcompany.extract(r.text)
            common.sql_main('zhilian', job_dict, url_get, job_id)

if __name__ == '__main__':
    b = sys.argv
    if len(b) > 1:
        url = b[1]
    else:
        url = 'http://company.zhaopin.com/CC120072290.htm'
    c_link = company_link(url)
    run_work(c_link)
