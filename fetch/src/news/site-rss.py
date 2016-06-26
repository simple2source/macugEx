# coding: utf-8
import feedparser
import json
from common import *
import os, chardet
import datetime
from time import mktime
from readability.readability import Document
from bs4 import BeautifulSoup
import socket
import MySQLdb
import common, logging
import sys
import articlefliter
reload(sys)
sys.setdefaultencoding('utf8')

# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'rss.log')
logging.config.dictConfig(log_dict)
logging.info('hahahahha, start rss')

# 配置文件解释


sql_config = common.sql_config
timeout = 10
socket.setdefaulttimeout(timeout)

# s = requests.Session()

# conf_dd = os.path.join(conf_dir, 'config.json')
# with open(conf_dd) as f:
#     conf = json.load(f)

db = MySQLdb.connect(**sql_config)
cursor = db.cursor()
sql_conf = """select `name`, `interval`, `full_text`, `rss_url` from news_info where `source` = 'RSS' and `interval` != '0' """
cursor.execute(sql_conf)
data = cursor.fetchall()
url_list = dict()
for i in data:
    if i[0] not in  url_list:
        url_list[i[0]] = dict()
    url_list[i[0]]['url'] = i[3]
    url_list[i[0]]['interval'] = i[1]
    url_list[i[0]]['full'] = i[2]

print url_list

def select(url, table):
    # db = sqlite3.connect('test.db')
    db = MySQLdb.connect(**sql_config)
    sql_sl = """ select url from `news` where url = '{}' limit 1  """.format(db.escape_string(url))
    cursor = db.cursor()
    cursor.execute(sql_sl)
    data = cursor.fetchall()
    # print url
    print len(data)
    if len(data) > 0:
        logging.info('source {} url {}  in mysql'.format(table, url))
        return True
    else:
        logging.info('source {} url {} not in mysql'.format(table, url))
        return False

def select_hour(name, hour):  # 看是否到了该重新抓取了，频率限制
    db = MySQLdb.connect(**sql_config)
    sql_sl = """ select update_time from `news_info` where `name` = '{}' limit 1  """.format(db.escape_string(name))
    cursor = db.cursor()
    cursor.execute(sql_sl)
    data = cursor.fetchall()
    # print url
    try:
        up_old = data[0][0]
        up_obj = up_old  # datetime.datetime.strptime(up_old, '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() - up_obj >= datetime.timedelta(hours=hour):
            logging.info('source {} is time to crawl'.format(name))
            print '```````````````````````000'
            return True
        else:
            logging.info('source {} not crawl now  '.format(name))
            print '+++++++++++++++++'
            return False
    except Exception, e:
        print Exception, e
        print '------------'
        logging.error('select hour error and msg is {}'.format(e))
        return True

try:
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()

except Exception, e:
    logging.error('Try to create table error and error msg is {}'.format(str(e)), exc_info=True)


# db = sqlite3.connect('test.db')
for i in url_list:
    print i
    i_num = 0  # 成功插入数
    i_num2 = 0 # 更新数，新增的文章
    logging.info('now is {} "s turn'.format(i))
    i_interval = url_list[i]['interval']
    i_total = 0  # 每次拉到的文章总数
    if select_hour(i, i_interval):
        try:
            a = feedparser.parse(url_list[i]['url'])
            i_total = len(a['entries'])
        except Exception, e:
            logging.error('feedparser err msg is {}'.format(str(e)), exc_info=True)
        for aa in a['entries']:
            url = aa.link.encode('utf8')
            keyword = ''
            if i == 'v2ex':
                url = url.split('#')[0]
            elif i.startswith('sina_'):  # 新浪rss输出有时候url不对
                logging.info('sina original url is {}'.format(url))
                try:
                    url = url.split('url=')[1]
                except:
                    pass
                if not url.startswith('http://tech.sina.com.cn'):
                    url = 'http://tech.sina.com.cn' + url
                logging.info('sina redirected url is {}'.format(url))
            title = aa.title.encode('utf8')
            print title
            content = aa.description.encode('utf8')
            if url_list[i]['full'] == 1:
                if aa.has_key('content'):
                    content = aa.content[0]['value'].encode('utf8')
                    logging.info('{} has full context output'.format(i))
            pub_time = aa.published_parsed
            pub_time = datetime.datetime.fromtimestamp(mktime(pub_time))
            print pub_time
            if not select(url, i):
                i_num2 += 1
                if url_list[i]['full'] != 1:
                    try:
                        if i == 'oschina blog':
                            url_2 = url + '?fromerr=dy4SuBAE'
                            r = common.get_request(url_2)
                        else:
                            r = common.get_request(url)
                        print r.url
                        print r.encoding
                        soup = BeautifulSoup(r.text.encode(r.encoding), 'html.parser')
                        keyword = soup.find('meta', {'name': 'keywords'})
                        print r.encoding
                        if keyword:
                            keyword = keyword.get('content')
                            keyword = keyword.encode('utf8', 'ignore')
                        else:
                            keyword = ''
                        try:
                            if i == 'phphub':
                                keyword = soup.find('div', {'class': 'meta inline-block'}).a.get_text()
                            elif i == 'css88':
                                keyword = soup.find('footer', {'class': 'entry-meta'}).find_all('a', {'rel': 'tag'})
                                keyword = ','.join([k.get_text().strip() for k in keyword])
                        except:
                            pass
                        content = Document(r.text.encode(r.encoding, 'ignore')).summary().encode('utf-8')
                        title = Document(r.text.encode(r.encoding)).short_title().encode('utf-8')
                        print title
                    except Exception, e:
                        logging.info('error msg is {}'.format(str(e)), exc_info=True)
                pub_time = datetime.datetime.strftime(pub_time,'%Y-%m-%d %H:%M:%S')
                print pub_time
                if articlefliter.comb(content, 200):
                    rate = -1
                else:
                    rate = 0
                l = [i, url, title, content, pub_time, keyword]
                l2 = []
                for iii in l:
                    l2.append(db.escape_string(iii))
                l2.append(rate)
                sql_in = """ insert into `news` (source, url, title, content, pub_time, keyword_exact, rating) values('{}', '{}','{}','{}','{}','{}','{}') """\
                        .format(*l2)
                try:
                    cursor.execute(sql_in)
                    i_num += 1
                    db.commit()
                    logging.info('insert url {} success'.format(url.encode("utf8")))
                except Exception, e:
                    print sql_in
                    print Exception, e
                    logging.error('try to execute sql insert error and error is {} url is {}'.format(str(e), url.encode('utf8')), exc_info=True)
        time_now = datetime.datetime.now()
        if i_num > 0:
            sql_up = """ update news_info SET `latest_num`='{}', `latest_time`='{}', `update_time` = '{}', `latest_total` = '{}', `latest_num2` = '{}' WHERE `name` = '{}'""".format(i_num, time_now, time_now, i_total, i_num2, i)
        else:
            sql_up = """ update news_info SET `update_time`='{}', latest_total='{}', latest_num2 = '{}' WHERE `name` = '{}'""".format(time_now, i_total, i_num2, i)
        cursor.execute(sql_up)
        db.commit()
db.close()

logging.info('one cycle done')
print 'done'
