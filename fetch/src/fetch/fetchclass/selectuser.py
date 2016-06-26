# encoding: utf-8

import json
import MySQLdb
import os, urlparse, random
import sys, re
import lib51search
import libcjolsearch
import libzhilian
import requests
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')


class Selcet_user(object):
    """挑选适合的cookie"""
    def __init__(self, source='', location='%', option='%'):
        # 先是 json_str
        self.option = option
        if self.option == 'buy':
            self.option = 'buy_num'
        elif self.option == 'pub':
            self.option = 'pub_num'
        else:
            print 'option input no correct'
        self.location = location
        self.source = source
        if self.source == 'cjol':
            self.source = 'zjol'
        if self.source == 'zhilian':
            self.source = 'zl'
        self.sql_config = {
                'host': "10.4.14.233",
                'user': "tuike",
                'passwd': "sv8VW6VhmxUZjTrU",
                'db': 'tuike',
                'charset': 'utf8'
            }
        self.cookie_dir = '/data/spider/cookie'
        self.c_list = []
        self.task = '/data/fetch/task/51/task_20_25.txt'

    def sql_select(self):
        """找到相符合 pub, buy的用户名"""
        db = MySQLdb.connect(**self.sql_config)
        sql = ''' select user_name from grapuser_info WHERE grap_source = '{}' and account_type = '购买账号'
        and account_mark like '%{}%' and {} > 0
        '''.format(self.source, self.location, self.option)
        if self.option == """pub_num""":
            sql += """ and provider like '%,pub' """
        cur = db.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        l = []
        for i in data:
            # print i
            l.append(i[0])
        # print data
        return l

    def sql_select3(self):
        """用户名，不管buy_num, pub_num"""
        db = MySQLdb.connect(**self.sql_config)
        sql = ''' select user_name from grapuser_info WHERE grap_source = '{}' and account_type = '购买账号'
        and account_mark like '%{}%'
        '''.format(self.source, self.location)
        if self.option == """pub_num""":
            sql += """ and provider like '%,pub' """
        cur = db.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        l = []
        for i in data:
            # print i
            l.append(i[0])
        # print data
        return l

    def sql_select2(self):
        """返回公司名称，用户名，密码的一个列表，用来 liblogin 调用登陆"""
        db = MySQLdb.connect(**self.sql_config)
        sql = ''' select grap_member, user_name, `password` from grapuser_info WHERE grap_source = '{}' and account_type = '购买账号'
        and account_mark like '%{}%' and {} > 0
        '''.format(self.source, self.location, self.option)
        if self.option == """pub_num""":
            sql += """ and provider like '%,pub' """
        cur = db.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        l = []
        for i in data:
            d = dict()
            d['company_name'] = i[0]
            d['user_name'] = i[1]
            d['password'] = i[2]
            l.append(d)
        # print data
        return l

    def sql_password(self, un= ''):
        """输入 用户名 un ，得到公司名称，密码 """
        db = MySQLdb.connect(**self.sql_config)
        sql = ''' select `grap_member`, `password` from grapuser_info WHERE user_name = '{}' '''.format(un)
        pw = ''
        cn = ''
        try:
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            cn = data[0][0]
            pw = data[0][1]
        except:
            print "can not find {} 's password in MySQL".format(un)
            pass
        return cn, pw



    def select_cookie(self, option=1):
        """挑选cookie, option 为1表示严格选择 buy pub num > 0 , 0 表示 不严格选择，用来先更新 buy pub num"""
        print '---------------'
        self.c_list = []
        #a = lib51down.down51job()
        # print os.walk(self.cookie_dir)
        for root, path, files in os.walk(self.cookie_dir):
            # print root, path, files, 99988888
            cookie_file_list = files
        cookie_file_list= [n for n in cookie_file_list if n.endswith('.txt')]
        cookie_51 = [n for n in cookie_file_list if n.startswith('51_')]
        # print cookie_51
        cookie_cjol = [n for n in cookie_file_list if n.startswith('cjol') ]

        cookie_zl = [n for n in cookie_file_list if n not in cookie_51 if n not in cookie_cjol ]
        # print cookie_zl
        # print cookie_cjol
        if option == 1:
            l = self.sql_select()  # 选择的都是可以购买的
        elif option == 0:
            l = self.sql_select3()  # 选择的是带vision,pub的
        avail_list = []
        if self.source == '51job':
            for c_51 in cookie_51:
                fpath = os.path.join(self.cookie_dir, c_51)
                # print fpath, 9999999999
                with open(fpath) as f:
                    ff = f.read()
                # print ff
                ck_dict = urlparse.parse_qs(ff)
                # print ck_dict
                if ck_dict.keys().count('UserName') == 1:
                    username=ck_dict['UserName'][0]
                    # print username
                    if username in l:
                        self.c_list.append(fpath)
        if len(self.c_list) > 0:
            for i in self.c_list:
                a = lib51search.job51search(fpath, '')
                a.load_cookie(i)
                if a.login_status_chk():
                    avail_list.append(i)
        elif self.source == 'zjol':
            for c_cjol in cookie_cjol:
                fpath = os.path.join(self.cookie_dir, c_cjol)
                # print fpath
                with open(fpath) as f:
                    ff = f.read()
                ck_dict = urlparse.parse_qs(ff)
                if ck_dict.keys().count(' CompanyID') == 1:
                    company_id = ck_dict[' CompanyID'][0]
                    if str(company_id) == '317080':
                        username = 'LHYS'
                    if str(company_id) == '308380':
                        username = 'qimingguanggao'
                    if username in l:
                        # print username
                        self.c_list.append(fpath)
            if len(self.c_list) > 0:
                for i in self.c_list:
                    a = libcjolsearch.mainfetch(i, '')
                    a.load_cookie(i)
                    if a.login_status_chk():
                        avail_list.append(i)
        elif self.source == 'zl':
            # print cookie_zl
            for c_z in cookie_zl:
                fpath = os.path.join(self.cookie_dir, c_z)
                # print fpath
                with open(fpath) as f:
                    ff = f.read()
                if c_z.split('.')[0] in l:
                    self.c_list.append(fpath)
            if len(self.c_list) > 0:
                avail_list = self.c_list
        # print(avail_list)
        return avail_list

    def avail_num(self, un=''):
        username = un
        sql =''' select {} from grapuser_info WHERE grap_source = '{}' and user_name = '{}'
        '''.format(self.option, self.source, username)
        num = 0
        try:
            db = MySQLdb.connect(**self.sql_config)
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            num = data[0][0]
        except:
            pass
        return num

    def num_update(self, source='', un='', ck_str=''):
        """ 需要传入再用的ck_str, source 来源 重新登录会踢其他用户下线 un 用户名"""
        s = requests.session()
        pub_num = 0
        buy_num = 0
        expired_day = '1999-9-9'
        try:
            if source == '51job':
                mysql_source = '51job'
                url = 'http://ehire.51job.com/Navigate.aspx?ShowTips=11&PwdComplexity=N'
                s.headers['cookie'] = ck_str
                s.headers['Host'] = 'ehire.51job.com'
                s.headers['Referer'] = 'http://ehire.51job.com/MainLogin.aspx'
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
                r = s.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                try:
                    pub_num = soup.find('span', {'id': 'Navigate_AvalidJobs'}).a.b.text
                    buy_num = soup.find('span', {'id': 'Navigate_AvalidResumes'}).a.b.text
                    expired_day = soup.find('span', {'id': 'Navigate_EndDate'}).get_text()
                    expired_day = re.search(r'\d.+\d', expired_day).group()
                    print pub_num, buy_num, 'pub_num, buy_num'
                except Exception, e:
                    print 'update error'
                    print Exception, str(e)
                    pass

            elif source == 'zhilian':
                mysql_source = 'zl'
                url = 'http://rd2.zhaopin.com/s/homepage.asp'
                s.headers['cookie'] = ck_str
                # s.headers['Host'] = 'rd2.zhaopin.com'
                s.headers['Host'] = 'rd.zhaopin.com'
                # s.headers['Referer'] = 'http://www.cjol.com/hr/'
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
                proxies = {
                  'http': 'http://10.4.16.39:8888',
                  'https': 'http://10.4.16.39:8888',
                }
                # r = s.get(url)
                # soup = BeautifulSoup(r.text, 'html.parser')
                url1 = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/JM114403938R90250002000_1_1?searchresume=1'
                r1 = s.get(url1, proxies=proxies)
                soup_1 = BeautifulSoup(r1.text, 'html.parser')
                try:
                    buy_num = soup_1.find('div', {'class': 'intro-span-right'}).span.get_text()
                except Exception, e:
                    print Exception, e
                    buy_num = '0'
                url2 = 'http://jobads.zhaopin.com/Position/PositionAdd'
                s.headers['Host'] = 'jobads.zhaopin.com'
                r2 = s.get(url2)
                soup_2 = BeautifulSoup(r2.text, 'html.parser')
                try:
                    pub_num = soup_2.find('input', {'name': 'PublicPoints'}).get('value')
                except Exception, e:
                    print Exception, e
                    pub_num = '0'
                print buy_num, pub_num

                # try:
                #     soup1 = soup.find_all('li', {'class': 'mcSeperatorLi'})
                #     for i in soup1:
                #         soup2 = i.find_all('li')
                #         for i2 in soup2:
                #             if u'还可发布职位：' in i2.get_text():
                #                 pub_num = i2.find('span').get_text()
                #             if u'剩余下载数：' in i2.get_text():
                #                 buy_num = i2.find('span').get_text()
                # except Exception, e:
                #     print Exception, str(e)
                #     pass

            elif source == 'cjol':
                mysql_source = 'zjol'
                url = 'http://newrms.cjol.com/Default'
                s.headers['cookie'] = ck_str
                s.headers['Host'] = 'newrms.cjol.com'
                s.headers['Referer'] = 'http://www.cjol.com/hr/'
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
                r = s.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                try:
                    soup1 = soup.find('div', {'class': 'homeserver-count'})
                    soup2 = soup1.find_next('div', {'class': 'homeserver-count'})
                    pub_num = soup1.p.em.get_text()
                    buy_num = soup2.p.em.get_text()
                    soup3 = soup.find('p', {'class': 'sv-rangetime f_l'})
                    expired_day = soup3.find_all('em')[1].get_text()
                except:
                    pass

            sql = """update grapuser_info set buy_num={}, pub_num={}, expire_time='{}' where user_name ="{}" and
                     grap_source = "{}";  """.format(buy_num, pub_num, expired_day, un, mysql_source)
            try:
                db = MySQLdb.connect(**self.sql_config)
                cur = db.cursor()
                aaa = cur.execute(sql)
                db.commit()
                db.close()
            except Exception, e:
                print Exception, str(e)
                pass
        except Exception, e:
            print Exception, str(e)
            pass

        return pub_num, buy_num



if __name__ == '__main__':
    p = Selcet_user('zhilian')
    # print p.location#.encode('utf-8')
    print p.source
    # p.sql_select()
    p.select_cookie()
