# encoding: utf8

# from __future__ import unicode_literals
import requests
import common
from bs4 import BeautifulSoup
import MySQLdb
import logging, re
import sys, json, os
import logging.config
reload(sys)
sys.setdefaultencoding('utf8')


with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'chuansong.log')
logging.config.dictConfig(log_dict)
logging.debug('hahahahha')


def url_cr(account):
    url = 'http://chuansong.me/account/' + str(account)
    return url


def link_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    ll = soup.find_all('a', {'class': 'question_link'})
    ll2 = ['http://chuansong.me' + i.get('href') + ',' + i.get_text().strip() for i in ll]
    logging.debug('get all link in one page is {}'.format(ll2))
    return ll2

def next_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    page = soup.find('span', {'style': 'font-size: 1em;font-weight: bold'})
    page_next = page.next_sibling.next_sibling
    if page_next.get_text() == '下一页':
        try:
            next_url = 'http://chuansong.me' + page_next.get('href')
            logging.info('next page url is "{}"'.format(next_url))
            return next_url
        except Exception as e:
            logging.error('get next page url error error msg is {}'.format(e))
            return None

def re_time(text):  # 文本中找出 日期
    p = re.compile('\d{4}-\d{2}-\d{2}')
    pp = re.search(p, text)
    if pp is None:
        pub_time = ''
    else:
        pub_time = pp.group()
    return pub_time


def page_parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', {'class': 'rich_media_content ', 'id': 'js_content'})
    content = unicode(content)
    title = soup.find('h2', {'class': 'rich_media_title'}).get_text().strip()
    # print title, content
    pub_time = re_time(html)
    logging.error('get pub_time is {}'.format(pub_time))
    return title, content, pub_time


def ad_remove(soup):
    # 百度广告是自动加载在图片上的，源码上找不到
    ll = soup.find_all('div', {'class': 'ad-widget-imageplus-sticker '
                                        'ad-widget-imageplus-sticker-theme-v2 ad-widget-imageplus-sticker-cut'})
    for i in ll:
        soup.decompose(i)
    return soup

def one_page(html, source):
    ll = link_list(html)
    common.rand_sleep(3, 1)
    for i in ll:
        url, title = i.split(',')
        logging.debug('next url is {}'.format(url))
        if not sql_se(source, title):
            r2 = common.get_request(url)
            title2, content, pub_time= page_parse(r2.text)
            common.sql_insert(source, url, title, content, pub_time, '')
        common.rand_sleep(6, 2)


def main(source):
    url = url_cr(source)
    logging.debug('chuansong url is {}'.format(url))
    r = common.get_request(url)
    if r:
        html = r.text
        one_page(html, source)
        try:
            url2 = next_page(html)
            logging.debug('page 2 url is {}'.format(url2))
            while url2:
                r2 = common.get_request(url2)
                html2 = r2.text
                one_page(html2, source)
                url2 = next_page(html2)
        except Exception as e:
            logging.error('err get next page msg is {}'.format(e), exc_info=True)

def sql_se(source, title):
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    sql = """select id from news where source = '{}' and title = '{}'""".format(source, MySQLdb.escape_string(title))
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) > 0:
        logging.info('source {} title {}  in mysql'.format(source, title))
        return True
    else:
        logging.info('source {} title {} not in mysql'.format(source, title))
        return False


def we_list():
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    sql_conf = """select `name` from news_info where `source` = 'WeChat' and `interval` != '0' """
    cursor.execute(sql_conf)
    data = cursor.fetchall()
    url_list = [i[0] for i in data]
    logging.debug('get all wechat id is {}'.format(url_list))
    return url_list


if __name__ == '__main__':
    account_list = we_list()
    for i in account_list:
        logging.info('now is {} turn'.format(i))
        main(i)
    # with open('nnn.html') as f:
    #     ff = f.read()
    # page_parse(ff)

