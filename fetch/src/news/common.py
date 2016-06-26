# encoding: utf8
import requests
import re, codecs, operator, MySQLdb
import random,time,sqlite3
import requests.packages.urllib3
import os
import smtplib,ConfigParser
from email.mime.text import MIMEText
import logging
import logging.config


headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    # 'Host':"www.huxiu.com",
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}
root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
# print conf_dir
basic_confpath=os.path.join(conf_dir,'basic.conf')
json_config_path = os.path.join(conf_dir, 'logging.json')
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')

# sql_config = {
#     'host': "localhost",
#     'user': "admin",
#     'passwd': "hick",
#     'db': 'tuike',
#     'charset': 'utf8',
# }
sql_config = {
    'host': "10.4.14.233",
    'user': "tuike",
    'passwd': "sv8VW6VhmxUZjTrU",
    'db': 'tuike',
    'charset': 'utf8',
}

def get_request(url, headers=headers, params='',cookies={}, timeout=5):
    s = requests.Session()
    requests.packages.urllib3.disable_warnings()
    logging.info('begin to get url {}'.format(url))
    flag = 0
    count = 0
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'http://' + url
    # try:
    #     headers['Host'] = url.split('/')[2]
    # except:
    #     pass
    while flag == 0:
        try:
            r = s.get(url, headers=headers, params=params, cookies=cookies, timeout=timeout, verify=False)
            print r.status_code
            if r.status_code in [200, 301, 302]:
                logging.info('get url {} status success, status code is {}'.format(url, r.status_code))
                flag = 1
                return r
            elif r.status_code == 404:
                return None
            else:
                count += 1
                logging.error('get url {} error status code is {}'.format(url, r.status_code))
                if count > 10:
                    return r
                flag = 0
                rand_sleep(5)
        except Exception, e:
            # print Exception, str(e)
            logging.error('get url error and msg is {}'.format(str(e)))
            count += 1
            if count > 3:
                return None
            flag = 0
            rand_sleep(5)

def post_request(url, data='', headers=headers):
    s = requests.Session()
    requests.packages.urllib3.disable_warnings()
    flag = 0
    count = 1
    while flag == 0:
        try:
            r = s.post(url, data=data, headers=headers, timeout=5)
            print r.status_code
            if r.status_code in [200, 301, 302]:
                flag = 1
                return r
            else:
                count += 1
                if count > 10:
                    return r
                flag = 0
                rand_sleep(5)
        except Exception, e:
            print Exception, str(e)
            flag = 0
            rand_sleep(2)


def rand_sleep(sec, min_sec=1):
    if sec > 0:
        sec = sec
    else:
        sec = 3
    sleepTime = random.random() * sec
    if sleepTime < min_sec:
        sleepTime += min_sec
    sleepTime = float('%0.2f' % sleepTime)
    print sleepTime
    logging.info('sleep time is {}'.format(sleepTime))
    time.sleep(sleepTime)

def sendEmail(moudle_name='', title='', message='',msg_type=0, des='T'):
  '''功能描述：通用发信模块，发送简要的email信息,
  新增加一参数，新增P报表'''
  try:
    if os.path.exists(basic_confpath):
      cf = ConfigParser.ConfigParser()
      cf.read(basic_confpath)
      server_host=cf.get('email','server')
      uname=cf.get('email','username')
      upass=cf.get('email','password')
      tmp_user=cf.get('email','default_users')
      tmp_puser=cf.get('email','product_users')
      default_list = []
      product_list = []
      for m in tmp_user.split(';'):
        if m and default_list.count(m) == 0:
          default_list.append(m)
      users= default_list
      #产品的邮箱地址
      for m in tmp_puser.split(';'):
        if m and product_list.count(m) == 0:
          product_list.append(m)
      pusers = product_list
      operation_users = ['jerry@tuikor.com', 'vinsonli@tuikor.com']
      if msg_type == 1 and not users:
        users=['kelvin@tuikor.com']
      if des == 'P':
        users=pusers + users
      elif des == 'op':
        users = pusers + operation_users + users
    else:
      logging.info('defaulte conf file not exist.')
      server_host='smtp.163.com'
      uname='hickwu@163.com'
      upass='HickWu608'
      users=['hick@tuikor.com']

    if server_host and uname and upass and users:
      msg = MIMEText(message, _subtype='html', _charset='UTF-8')
      #msg['From'] = uname
      msg['Subject'] = title
      msg['From'] = uname
      msg['To'] = ';'.join(users)

      s = smtplib.SMTP()
      #s.set_debuglevel(1)
      s.connect(server_host)
      s.login(uname,upass)
      s.sendmail(uname, users, msg.as_string())
      s.close()
      return True
    else:
      return False
  except Exception,e:
    logging.debug('error msg is %s ' % str(e))
    return False

def select(url, table):
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

def re_time(text):  # 文本中找出 日期
    p = re.compile('\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}')
    pp = re.search(p, text)
    if pp is None:
        pub_time = ''
    else:
        pub_time = pp.group()
    return pub_time

def sql_insert(source, url, title, content, pub_time, keyword):
    try:
        db = MySQLdb.connect(**sql_config)
        cursor = db.cursor()
        l = [source, url, title, content, pub_time, keyword]
        l2 = []
        for i in l:
            l2.append(db.escape_string(i))
        sql_in = """ insert into `news` (source, url, title, content, pub_time, keyword_exact)
        values('{}', '{}','{}','{}','{}','{}') """.format(*l2)
        cursor.execute(sql_in)
        db.commit()
        logging.info('insert success url is {}'.format(url))
        db.close()
        return True
    except Exception, e:
        print Exception, e
        logging.error('insert mysql error {}'.format(sql_in), exc_info=True)
        return False