# encoding: utf8
import common
import random
import json
from bs4 import BeautifulSoup
import requests
import os, copy
import re
import MySQLdb
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging, logging.config
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
cf = logging.FileHandler('itjuzi.log')
cf.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
cf.setFormatter(formatter)
logger.addHandler(cf)

def find_all_link(html):
    p = re.compile("http://www.itjuzi.com/company/\d+")
    hh = re.findall(p, html)
    hh2 = list(set(hh))
    return hh2


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    phone, email, company_url, name, process, city, district, addr = '', '', '', '', '', '', '', ''
    try:
        phone = soup.find('i', {'class': 'fa fa-phone'}).find_next().get_text()
        phone = zan_wei(phone)
    except:
        logger.warning('find phone error', exc_info=True)
        pass
    try:
        email = soup.find('i', {'class': 'fa fa-envelope'}).find_next().get_text()
        email = zan_wei(email)
    except:
        logger.warning('find email error', exc_info=True)
        pass
    try:
        addr = soup.find('i', {'class': 'fa fa-map-marker'}).find_next().get_text()
        addr = zan_wei(addr)
    except:
        logger.warning('find address error', exc_info=True)
        pass
    try:
        loc = soup.find('span', {'class': 'loca c-gray-aset'}).get_text().replace('\n', '')
        loc1 = loc.split('·')
        district = loc1[1]
        city = loc1[0]
    except:
        logger.warning('find location error', exc_info=True)
        pass
    try:
        company_url = soup.find('a', {'class': 'weblink marl10'}).get('href')
    except:
        logger.warning('find url error', exc_info=True)
        pass
    try:
        name = soup.find('div', {'class': 'line-title'}).span
    except:
        logger.warning('find name title error', exc_info=True)
        pass
    try:
        process = name.span.extract().get_text().strip().strip(')').strip('(')
    except:
        logger.warning('find process error', exc_info=True)
        pass
    try:
        name = name.get_text().strip()
    except:
        logger.warning('find name error', exc_info=True)
        pass
    print phone, email, company_url, name, process, city, district, addr
    return [phone, email, company_url, name, process, city, district, addr]


def zan_wei(text):
    if text == u'暂未收录':
        text = ''
    return text

def sql_in(juzi_id, ll):
    phone, email, company_url, name, process, loc, district, addr = ll
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    sql = """insert into itjuzi (juzi_id, `name`, phone, email, url, process, loc, district,
              addr) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
              """.format(juzi_id, name, phone, email, company_url, process, loc, district, addr)
    print sql
    cursor.execute(sql)
    db.commit()
    db.close()

def main():
    rootdir = os.getcwd()
    print rootdir
    try:
        company_list_dir = os.path.join(rootdir, 'juzi')
        # for subdir, dirs, files in os.walk(company_list_dir):
        #     for file in files:
        #         logger.info('current file is {}'.format(file))
        #         fff = os.path.join(subdir, file)
        #         with open(fff) as f:
        #             ff = f.read()
        #         url_list = find_all_link(ff)
        #         print url_list
        # for i in url_list:
        for num in xrange(35770, 36000):
            i = 'http://www.itjuzi.com/company/' + str(num)
            try:
                logger.info('current url is {}'.format(i))
                juzi_id = i.replace('http://www.itjuzi.com/company/', '')
                if not sql_sel(juzi_id):
                    logger.info('try to insert {} into mysql'.format(juzi_id))
                    gs_fp = os.path.join(rootdir, 'juzicompany')
                    if not os.path.exists(gs_fp):
                        os.makedirs(gs_fp)
                    job_id = str(juzi_id)
                    job_id = job_id.rjust(5, '0')
                    store_path = os.path.join(gs_fp,job_id[0:3], job_id +'.html')
                    father_dir=os.path.dirname(store_path)
                    if not os.path.exists(father_dir):
                        os.makedirs(father_dir)
                    r = common.get_request(i)
                    if r:
                        with open(store_path, 'w+') as f:
                            f.write(r.text)
                        ll = parse_page(r.text)
                        sql_in(juzi_id, ll)
                        common.rand_sleep(5, 2)
            except:
                logger.error('something wrong ', exc_info=True)
    except:
        logger.error('something wrong ', exc_info=True)

def sql_sel(url):
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    sql = 'select id from itjuzi where juzi_id = "{}"'.format(MySQLdb.escape_string(url))
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    print data
    if len(data) > 0:
        logger.info('url {} already in mysql'.format(url))
        return True
    else:
        logger.info('url {} not in mysql'.format(url))
        return False


if __name__ == '__main__':
    # with open('iitt.html') as f:
    #     ff = f.read()
    # parse_page(ff)
    main()