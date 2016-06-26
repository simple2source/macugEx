# encoding: utf-8

"""
登陆相关函数，还有检查登陆态的
"""
import requests
from bs4 import BeautifulSoup
import urllib
import random, time, json, logging, os
import logging.config
import common
import sqlite3
# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'autologin.log')
logging.config.dictConfig(log_dict)
logging.debug('hahahahha')


class Login51():
    def __init__(self, cn='', un='', pw=''):
        """输入参数，cn company name, un user name, pw password"""
        self.s = requests.Session()
        self.s.trust_env = False
        self.payload = {
            "ctmName": "%E5%A4%A7%E6%B5%B7%E6%8A%95%E8%B5%84%E9%A1%B9%E7%9B%AE%E4%B8%80",
            "userName":"dhtz455",
            "password": "supin2015",
            "checkCode": "",
            "oldAccessKey": "f5dfb7aa4300490",
            "langtype": "Lang=&amp;Flag=1",
            "isRememberMe": "true",
            "sc": "69452d17c390979e",
            "ec": "33609d56e0e84397a979223ee92f8708",
            "returl":"",
        }
        self.header = {
            'Host': 'ehirelogin.51job.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://ehire.51job.com/MainLogin.aspx',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length':  '299',
        }
        self.url = 'https://ehirelogin.51job.com/Member/UserLogin.aspx'
        self.company_name = cn
        self.user_name = un
        self.password = pw

    def login(self):
        """return avail cookie string"""
        self.payload['ctmName'] = urllib.quote(self.company_name)
        self.payload['userName'] = self.user_name
        self.payload['password'] = self.password
        r2 = self.s.get('http://ehire.51job.com/MainLogin.aspx')
        cookie_string = ''
        if r2.text.find('imgCheckCodeCN') > 0:
            return None
        soup = BeautifulSoup(r2.text, 'html.parser')
        try:
            self.payload['oldAccessKey'] = soup.find('input', {'id': 'hidAccessKey'}).get('value')
        except Exception, e:
            print 'get access key error'
            logging.warning('get access key error, msg is {}'.format(str(e)), exc_info=True)
        try:
            self.payload['ec'] = soup.find('input', {'id': 'hidEhireGuid'}).get('value')
        except Exception, e:
            print 'get access key error'
            logging.warning('get access key error, msg is {}'.format(str(e)), exc_info=True)
        try:
            self.payload['sc'] = soup.find('input', {'id': 'fksc'}).get('value')
        except Exception, e:
            print 'get access key error'
            logging.warning('get access key error, msg is {}'.format(str(e)), exc_info=True)
        r = self.s.post(self.url, headers=self.header, data=self.payload, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        if r.text.find(u'<U>强制下线</U></font>') > 0:
            print '-------kick previous user offline-------'
            logging.info('51job kick previous user offline')
            url_kick = r.url
            view_state = soup.find('input', {'name': '__VIEWSTATE'}).get('value')
            event_target = 'gvOnLineUser'
            event_argument = 'KickOut$0'
            payload_kick = {
                '__EVENTTARGET': event_target,
                '__EVENTARGUMENT': event_argument,
                '__VIEWSTATE': view_state,
            }
            self.header['Referer'] = url_kick
            '''踢之前的用户下线'''
            r2 = self.s.post(url_kick, data=payload_kick, headers=self.header)
        ck = requests.utils.dict_from_cookiejar(self.s.cookies)
        cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()])
        # print cookie_string
        return cookie_string

    def check_login(self, ck_str=''):
        """check username if is online"""
        headers = {
            'Host': 'ehire.51job.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://ehire.51job.com/Candidate/SearchResume.aspx',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        chk_url = r'http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=10010'
        self.s.headers['cookie'] = ck_str
        r = self.s.get(chk_url, headers=headers)
        if r.text.find(u'登录') < 0:
            return True
        else:
            return False

    def main(self, sleep=0):
        """sleep 为设定的睡眠时间，爬虫需要，购买应该不需要等待, 设定大于10 才睡眠"""
        # 这里不作cookie ，user 选择逻辑，尝试登录user 3次，成功return cookie string
        count = 0
        cookie_string = ''

        try:
            db = sqlite3.connect(common.stat_db_path)
            cursor = db.cursor()
            sql_cr = ''' create table If not EXISTS job51
                    (
                    username varchar(255),
                    times INTEGER DEFAULT 0,
                    add_time timestamp DEFAULT (datetime('now','localtime'))
                    )'''
            cursor.execute(sql_cr)
            db.commit()
            db.close()
        except Exception, e:
            logging.error('sqlite3 create table error and error msg is {}'.format(str(e)), exc_info=True)
        if sleep > 10:
            min_sleep = random.randint(10, sleep)
            time.sleep(min_sleep * 60)
        while count <= 3:
            try:
                cookie_string = self.login()
                if cookie_string is None:
                    break
                if self.check_login(ck_str=cookie_string):
                    logging.info('51job {} auto login success, times is {}'.format(self.user_name, count))
                    try:
                        db = sqlite3.connect(common.stat_db_path)
                        cursor = db.cursor()
                        sql = """ insert into job51 (username, times) values('{}', {}) """.format(self.user_name, count)
                        cursor.execute(sql)
                        db.commit()
                        db.close()
                    except Exception, e:
                        logging.error('auto login insert sqlite3 error and err msg is {}'.format(str(e)), exc_info=True)
                    break
                else:
                    time.sleep(30) # 睡眠30秒后再重试
                    count += 1
            except Exception, e:
                logging.warning('51 auto login error and error msg is {}'.format(str(e)))
                pass
        return cookie_string


class LoginZL(object):
    def __init__(self, cn='', un='', pw=''):
        """输入参数，cn company name, un user name, pw password"""
        self.s = requests.Session()
        self.s.trust_env = False
        self.company_name = cn
        self.user_name = un
        self.password = pw

    def login(self):
        pass

    def check_login(self, ck_str=''):
        """check username if is online"""
        headers = {
            'Host': 'rd.zhaopin.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        proxies = {
          'http': 'http://183.131.144.102:8081',
          'https': 'http://183.131.144.102:8081',
            }
        chk_url = r'http://rd.zhaopin.com/resumepreview/resume/viewone/2/JM114403938R90250002000_1_1?searchresume=1'
        self.s.headers['cookie'] = ck_str
        r = self.s.get(chk_url, headers=headers, proxies=proxies)
        if r.text.find(u'登录') < 0:
            return True
        else:
            return False

    def main(self, sleep=0):
        pass


class LoginCJOL(object):
    def __init__(self, cn='', un='', pw=''):
        """输入参数，cn company name, un user name, pw password"""
        self.s = requests.session()
        self.company_name = cn
        self.user_name = un
        self.password = pw

    def login(self):
        pass

    def check_login(self, ck_str=''):
        """check username if is online"""
        headers = {
            'Host': 'newrms.cjol.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'http://newrms.cjol.com/SearchEngine/List?fn=d',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        chk_url = r'http://newrms.cjol.com/resume/detail-1'
        self.s.headers['cookie'] = ck_str
        r = self.s.get(chk_url, headers=headers)
        if r.text.find(u'登录') < 0:
            return True
        else:
            return False

    def main(self, sleep=0):
        pass


if __name__ == '__main__':
    a = Login51(cn='大海投资项目二', un='dhtz963', pw='supin2015')
    a.login()