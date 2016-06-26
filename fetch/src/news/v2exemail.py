# encoding: utf8

import common
from bs4 import BeautifulSoup
import re
import MySQLdb
import datetime
import logging, logging.config
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
cf = logging.FileHandler('v2exemail.log')
cf.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
cf.setFormatter(formatter)
logger.addHandler(cf)


def getpage(page):
    url = 'http://www.v2ex.com/go/cv?p={}'.format(page)
    r = common.get_request(url)
    return r

def pageparse(html):
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('span', {'class': 'item_title'})
    b = ['http://www.v2ex.com' + i.a.get('href') for i in a]
    logger.info('get url list is {}'.format(str(b)))
    print b
    return b

def content(html):
    soup = BeautifulSoup(html, 'html.parser')
    # print soup
    a = soup.find('div', {'id': 'Main'})
    # print a
    b = a.find_all('div', {'class': 'box'})[1]
    # print b
    b2 = unicode(b)
    return b2


def get_page_one(url):
    r2 = common.get_request(url)
    cc = content(r2.text)
    # print cc
    if morepage(r2.text):
        common.rand_sleep(3, 2)
        r3 = common.get_request(url + '?p=1')  # 假如有两页
        logger.info('{} has two page, try to get page one'.format(url))
        cc += content(r3.text)
    dd = common.re_email(cc)
    print dd
    ee = list(set(dd))
    ff = ','.join(ee)
    return ff

def morepage(text):
    if text.find('class="page_current">') > 0:
        return True
    else:
        return False

def run(page):
    r = getpage(page)
    url_list = pageparse(r.text)
    for i in url_list:
        url = i.split('#')[0]
        common.rand_sleep(6, 2)
        ff = get_page_one(url)
        if not sql_sel(url):
            sql_in(url, ff)

def sql_in(url, email_str):
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    if not sql_sel(url):
        logger.info('trying to insert url {} and email str {}'.format(url, email_str))
        sql = "insert into v2exemail (url, email) values ('{}', '{}')".format(
            MySQLdb.escape_string(url), MySQLdb.escape_string(email_str))
        cursor.execute(sql)
        db.commit()
        db.close()


def sql_sel(url):
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    sql = 'select id from v2exemail where url = "{}"'.format(MySQLdb.escape_string(url))
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

def main():
    for i in range(60, 102):
        try:

            logger.info('now page is ' + str(i))
            run(i)
        except Exception as e:
            logger.error('err {}'.format(e), exc_info=True)

if __name__ == '__main__':
    main()
    # aaa = 'abc@gmail.com'
    # aaa = ' <a href="mailto:q@zhihu.com" ta'
    # re_email(aaa)