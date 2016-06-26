#!/usr/bin/env python
# encoding: utf-8

"""从 redis 中找用户名，废弃之前的文件保存方式。
抓取 选择账号的时候，需要从 cookie_expired 里面检查， 假如已经在集合里面
选择另一个账号，
cookie_expired  --redis set key
    用户登陆态失效的时候，从里面移除，选择另一个账号，（问题，账号数会越来越少）或者还是等待人工登陆
    达到限额的时候，从里面移除
（另一种方案，需要定时任务
每个小时从 MySQL 里面找出所有账号，然后覆盖redis里面的key cookies_user_all，
没有登录的尝试自动登陆， 登陆3次不行就发邮件，
选择账号的时候就可以直接从里面挑，抓取还是那样，用集合保存已经选择了的key，账号已经选择了的就直接不管了）

方案， 爬虫的，一小时检查一次登录态，抓取程序不管登录态的事，用redis 控制 每个爬虫不会用到相同的cookie，
cookie失效就直接丢弃，更换可用的cookie， 购买的跟之前相同，就改为不从文件中读取

多进程可以用相同的账号。 这边不检查登录态了，
爬虫那边登录态失效就应该在redis坐标记, cookie_expired 就是过期了的用户名
定了2个 redis hash， 存储 redis_key 创建的时间，和失效的时间。选择的时候就比较两个，假如创建时间大于
失效时间，就可以继续检查登录态了。
"""
import MySQLdb
import os, random
import sys, redis
import liblogin
import requests
from bs4 import BeautifulSoup
import datetime
import logging, json
import common
reload(sys)
sys.setdefaultencoding('utf8')
import logging.config



class Manage(object):
    def __init__(self, source='', location='', option='', num=''):
        # source 来源， option buy pub down， num MySQL 购买数量
        self.source = source
        self.option = option
        self.num = num
        self.location = location
        # self.username = username
        self.config={
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            #'connection_pool': self.pool
        }
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.not_write_path = os.path.join(self.path, 'not_write_in_redis.txt')
        self.error_path = os.path.join(self.path, 'redis_error.txt')
        self.pool = redis.ConnectionPool(**self.config)
        self.r = redis.StrictRedis(connection_pool=self.pool, **self.config)
        self.sql_config = common.sql_config
        if self.source == 'cjol':
            self.source = 'zjol'
        if self.source == 'zhilian':
            self.source = 'zl'
        if self.option == 'buy':
            self.option = 'buy_num'
        elif self.option == 'pub':
            self.option = 'pub_num'
        self.all_account = ''
        if self.source == '51job':
            self.redis_key_pre = 'cookie51_'
        elif self.source == 'zl':
            self.redis_key_pre = 'cookiezl_'
        elif self.source == 'zjol':
            self.redis_key_pre = 'cookiecjol_'
        # init other log
        with open(common.json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.FileHandler(os.path.join(common.log_dir, 'account.log')))
        # log_dict = json.loads(ff)
        # log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'account.log')
        # logging.config.dictConfig(log_dict)
        # logging.debug('hahahahha')



    def cookie_choose(self, option=0):
        # 选择对应的账号
        """挑选cookie, option 为1表示严格选择 buy pub num > 0 , 0 表示 不严格选择，用来先更新 buy pub num"""
        # print '------selecting cookies---------'
        logging.info('begin to select cookie')
        s = requests.session()
        l = self.sql_select(option)  # 选择的都是可以购买的
        avail_list = []
        if len(l) > 0:
            for user in l:
                if self.redis_exist(user):
                    ck_str = self.redis_ck_get(user)
                    company_name, password = self.sql_password(user)
                    if self.source == '51job':
                        a = liblogin.Login51(company_name.encode('utf-8'), user, password)
                    elif self.source == 'zl':
                        a = liblogin.LoginZL(company_name.encode('utf-8'), user, password)
                    else:
                        a = liblogin.LoginCJOL(company_name.encode('utf-8'), user, password)
                    if a.check_login(ck_str):
                        if self.source == '51job':
                            if a.check_login(ck_str, op=2):   #这里检查一下是否账号能搜索
                                avail_list.append(user)
                        else:
                            avail_list.append(user)
                    else:
                        ck_str2 = a.main()
                        if a.check_login(ck_str2):
                            if self.source == '51job':
                                if a.check_login(ck_str2, op=2):  # 这里检查一下是否账号能搜索
                                    avail_list.append(user)
                            else:
                                avail_list.append(user)
                            self.redis_ck_set(user, ck_str2)
        return avail_list

    def redis_ck_set(self, username, ck_str):
        # 用redis hash 存储 ck为ck_str mo为修改时间，ex过期时间
        redis_key = self.redis_key_pre + username
        self.r.hmset(redis_key, {'ck': ck_str.strip(), 'mo': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def redis_ck_get(self, username):
        # 根据用户名找 cookie
        redis_key = self.redis_key_pre + username
        ck_str = ''
        if self.redis_exist(username):
            ck_str = self.r.hget(redis_key, 'ck').strip()
        return ck_str

    def redis_ck_ex(self, username):
        # 设置过期时间
        expired_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        redis_key = self.redis_key_pre + username
        self.r.hset(redis_key, 'ex', expired_time)
        return True

    def redis_compare(self, username):
        redis_key = self.redis_key_pre + username
        add_time = self.r.hget(redis_key, 'mo')
        ex_time = self.r.hget(redis_key, 'ex')
        if add_time and ex_time:
            add_timeobj = datetime.datetime.strptime(add_time, '%Y-%m-%d %H:%M:%S')
            ex_timeobj = datetime.datetime.strptime(ex_time, '%Y-%m-%d %H:%M:%S')
            if add_timeobj > ex_timeobj:
                return True  # 修改时间比过期时间新
            else:
                return False
        else:
            return True


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
            db.close()
        except Exception, e:
            logging.warning('avail_num error and error msg is {}'.format(str(e)))
            pass
        return num


    def redis_user(self, username, ck_str=''):
        # 从redis中找相应的账号 cookie， 有ck_str就是在redis设置该 user 的cookie
        redis_key = self.redis_key_pre + username
        if len(ck_str) == 0:
            ck_str = self.r.get(redis_key)
            return ck_str
        elif len(ck_str) > 0:
            self.r.set(redis_key, ck_str)
            self.redis_addtime(username)
            return True

    def redis_exist(self, username):
        redis_key = self.redis_key_pre + username
        if self.r.exists(redis_key):
            return True
        else:
            return False

    def redis_picked(self, key='', op=1):
        """op为 1 增加  op 为0 移除
        爬虫检查登陆态，假如失效了，重试登陆后仍然失败，就加到cookie_expired 里面"""
        if op == 1:
            self.r.sadd('cookie_expired', key)
        else:
            self.r.srem('cookie_expired', key)

    def redis_ismen(self, key=''):
        return self.r.sismember('cookie_expired', key)

    def redis_addtime(self, username='', op=1):
        redis_key = self.redis_key_pre + username
        if op == 1: # 1表示设置 addtime redis key的修改时间
            self.r.hset('cookie_addtime', redis_key, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return True
        else:
            t = self.r.hget('cookie_addtime', redis_key)  # 读取时间
            return t

    def redis_expired_time(self, username='', op=1):
        redis_key = self.redis_key_pre + username
        if op == 1: # 1表示设置 addtime redis key的修改时间
            self.r.hset('cookie_extime', redis_key, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return True
        else:
            t = self.r.hget('cookie_extime', redis_key)  # 读取时间
            return t


    def sql_select(self, op=0):
        """找到相符合 pub, buy的用户名, op=1 表示为选择相应num需大于0， op=0对num 不作限制"""
        l = []
        try:
            db = MySQLdb.connect(**self.sql_config)
            sql = ''' select user_name from grapuser_info WHERE grap_source = '{}' and account_type = '购买账号'
            and account_mark like '%{}%'
            '''.format(self.source, self.location)
            if op == 1:
                sql += """ and {} > 0 """.format(self.option)
            if self.option == "pub_num":
                sql += """ and provider like '%,pub' """
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()

            for i in data:
                # print i
                l.append(i[0])
            # print data
        except Exception, e:
            logging.warning('sql select error and msg is {}'.format(str(e)), exc_info=True)
        return l

    def sql_passwork2(self):
        """返回公司名称，用户名，密码的一个列表，用来 liblogin 调用登陆"""
        l = []
        try:
            db = MySQLdb.connect(**self.sql_config)
            sql = ''' select grap_member, user_name, `password` from grapuser_info WHERE grap_source = '{}'
            and account_type = '购买账号'
            and account_mark like '%{}%' and {} > 0
            '''.format(self.source, self.location, self.option)
            if self.option == """pub_num""":
                sql += """ and provider like '%,pub' """
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            db.close()
            for i in data:
                d = dict()
                d['company_name'] = i[0]
                d['user_name'] = i[1]
                d['password'] = i[2]
                l.append(d)
                # print data
        except Exception, e:
            logging.warning('error and error msg is {}'.format(str(e), exc_info=True))
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
            db.close()
            cn = data[0][0]
            pw = data[0][1]
        except:
            # print "can not find {} 's password in MySQL".format(un)
            logging.warning("can not find {} 's password in MySQL".format(un), exc_info=True)
            pass
        return cn, pw

    def sql_password3(self):
        """返回MySQL里面能操作所有的用户名列表"""
        sql = ''' select `grap_source`, `user_name` from grapuser_info where account_type = '购买账号' '''
        if len(self.location) > 0:
            sql += """ and account_mark like '%{}%' """.format(self.location)
        l = []
        try:
            db = MySQLdb.connect(**self.sql_config)
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            db.close()
            for i in data:
                if i[0] == '51job':
                    redis_key_pre = 'cookie51_'
                elif i[0] == 'zl':
                    redis_key_pre = 'cookiezl_'
                elif i[0] == 'zjol':
                    redis_key_pre = 'cookiecjol_'
                redis_key = redis_key_pre + i[1]
                l.append(redis_key)
        except:
            logging.warning("can not find username in MySQL")
            pass
        return l

    def num_update(self, source='', un='', ck_str=''):
        """ 需要传入再用的ck_str, source 来源 重新登录会踢其他用户下线 un 用户名"""
        s = requests.session()
        s.trust_env = False
        pub_num = 0
        buy_num = 0
        try:
            if source == '51job':
                mysql_source = '51job'
                url_b = 'http://ehire.51job.com/CommonPage/JobsDownNumbList.aspx'  #从这里读取购买余额
                url_p = 'http://ehire.51job.com/CommonPage/JobsPostNumbList.aspx'  #从这里读取发布余额
                s.headers['cookie'] = ck_str
                s.headers['Host'] = 'ehire.51job.com'
                s.headers['Referer'] = 'http://ehire.51job.com/MainLogin.aspx'
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
                try:
                    r = s.get(url_b)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    soup_b = soup.find('tr', {'class':'text'}).find_all('td')[2]
                    buy_num = soup_b.get_text()
                except Exception as e:
                    logging.error('cannot find buynum msg is {}'.format(e), exc_info=True)
                try:
                    r = s.get(url_p)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    soup_p = soup.find_all('b', {'class': 'info_att'})[0]   # 只计算社会岗位
                    pub_num = soup_p.get_text()
                except Exception as e:
                    logging.error('cannot find pubnum error msg is {}'.format(e), exc_info=True)


            elif source == 'zhilian' or source == 'zl':
                mysql_source = 'zl'
                proxies = {
                  'http': 'http://10.4.16.39:8888',
                  'https': 'http://10.4.16.39:8888',
                    }
                url = 'http://rd2.zhaopin.com/s/homepage.asp'
                s.headers['cookie'] = ck_str
                # s.headers['Host'] = 'rd2.zhaopin.com'
                s.headers['Host'] = 'rdsearch.zhaopin.com'
                s.headers['Referer'] = 'http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd'
                # s.headers['Referer'] = 'http://www.cjol.com/hr/'
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
                # r = s.get(url)
                # soup = BeautifulSoup(r.text, 'html.parser')
                # url1 = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/JM114403938R90250002000_1_1?searchresume=1'
                url1 = 'http://rdsearch.zhaopin.com/Json/CompanyInfo'
                r1 = s.get(url1, proxies=proxies)
                # soup_1 = BeautifulSoup(r1.text, 'html.parser')
                try:
                    # buy_num = soup_1.find('div', {'class': 'intro-span-right'}).span.get_text()
                    buy_num = r1.json()['DownloadBalanceCount']
                except Exception, e:
                    logging.error('get zhilian buy_num error msg is {} '.format(e), exc_info=True)
                    buy_num = '0'
                url2 = 'http://jobads.zhaopin.com/Position/GetContractLeftPoints'
                s.headers['Referer'] = 'http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd'
                s.headers['Host'] = 'jobads.zhaopin.com'
                r2 = s.get(url2, proxies=proxies)
                # soup_2 = BeautifulSoup(r2.text, 'html.parser')
                try:
                    # pub_num = soup_2.find('input', {'name': 'PublicPoints'}).get('value')
                    pub_num = 0
                    for i in r2.json():
                        pub_num += i['leftP']
                except Exception, e:
                    # print Exception, e
                    logging.warning('update zhilian num error, msg is {}'.format(str(e)), exc_info=True)
                    pub_num = '0'
                # print buy_num, pub_num

            elif source == 'cjol' or source == 'zjol':
                mysql_source = 'zjol'
                url = 'http://newrms.cjol.com/Default'
                s.headers['cookie'] = ck_str
                s.headers['Host'] = 'newrms.cjol.com'
                s.headers['Referer'] = 'http://www.cjol.com/hr/'
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
                try:
                    r = s.get(url)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    soup1 = soup.find('div', {'class': 'homeserver-count'})
                    soup2 = soup1.find_next('div', {'class': 'homeserver-count'})
                    pub_num = soup1.p.em.get_text()
                    buy_num = soup2.p.em.get_text()
                except Exception, e:
                    logging.warning('update cjol num error, msg is {}'.format(str(e)), exc_info=True)

            sql = """update grapuser_info set buy_num={}, pub_num={} where user_name ="{}" and
                     grap_source = "{}";  """.format(buy_num, pub_num, un, mysql_source)
            try:
                db = MySQLdb.connect(**self.sql_config)
                cur = db.cursor()
                aaa = cur.execute(sql)
                db.commit()
                db.close()
            except Exception, e:
                # print Exception, str(e)
                logging.warning('update mysql error, msg is {}'.format(str(e)), exc_info=True)
                pass
        except Exception, e:
            # print Exception, str(e)
            logging.warning('error, msg is {}'.format(str(e)), exc_info=True)
            pass

        return pub_num, buy_num


    def account_all(self):
        """跑一次将51的登陆态搞上去，检查MySQL里面所有账号的登录态，假如没有登陆的话就尝试自动登陆（51），登陆不成功的发告警邮件
        已登录的账号加入到redis key cookie_logined 中"""
        try:
            db = MySQLdb.connect(**self.sql_config)
            sql = ''' select user_name, `grap_source` from grapuser_info WHERE account_type = '购买账号' '''
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            db.close()
            data2 = list(data)
            for i in data:
                if i[1] == '51job':
                    redis_key_pre = 'cookie51_'
                    redis_key = redis_key_pre + i[0]
                    if self.r.exists(redis_key):    # 保证能在redis中找到相应的cookie字符串
                        a = liblogin.Login51()
                        ck_str = self.r.get(redis_key)
                        a.check_login(ck_str)
                        if a.check_login(ck_str):
                            data2.remove(i)
                            self.r.sadd('cookie_logined', redis_key)
                        else:
                            cn, pw = self.sql_password(i[0])
                            a = liblogin.Login51(cn=cn, un=i[0], pw=pw)
                            ck_str = a.main()   # 这里那边尝试登陆3次
                            if len(ck_str) > 0:
                                self.redis_ck_set(i[0], ck_str)
                                data2.remove(i)
                elif i[1] == 'zl':
                    redis_key_pre = 'cookiezl_'
                    redis_key = redis_key_pre + i[0]
                    if self.r.exists(redis_key):
                        a = liblogin.LoginZL()
                        ck_str = self.r.get(redis_key)
                        a.check_login(ck_str)
                        if a.check_login(ck_str):
                            data2.remove(i)
                            self.r.sadd('cookie_logined', redis_key)
                elif i[1] == 'zjol':
                # if i[1] == 'zjol':
                    redis_key_pre = 'cookiecjol_'
                    redis_key = redis_key_pre + i[0]
                    if self.r.exists(redis_key):
                        a = liblogin.LoginCJOL()
                        ck_str = self.r.get(redis_key)
                        if a.check_login(ck_str):
                            data2.remove(i)
                            self.r.sadd('cookie_logined', redis_key)
        except Exception, e:
            logging.warning('error, msg is {}'.format(str(e)), exc_info=True)

        print data2  # 没有登陆的账号，发告警邮件用， 这里不用发邮件了




    def sql_num(self, username='', time_period=0, num=0):
        """
        :param username: 用户名
        :param time_period: 设定的时间段，一定要是秒数
        :return: 一定时间段内设定秒数 里面 用户名的抓取总数
        """
        time_str = (datetime.datetime.now()-datetime.timedelta(seconds=time_period)).strftime('%Y-%m-%d %H:%M:%S')
        sql = """select sum(num) from stats WHERE ext1 = "{}" and stat_time > '{}' """.format(username, time_str)
        l_num = 0
        # print sql
        if time_period == 0 or num == 0:
            return True
        else:
            try:
                sql_config = self.sql_config
                # sql_config = {
                # 'host': "localhost",
                # 'user': "testuser",
                # 'passwd': "",
                # 'db': 'reportdb',
                # 'charset': 'utf8'
                # }
                db = MySQLdb.connect(**sql_config)
                cur = db.cursor()
                cur.execute(sql)
                data = cur.fetchall()
                if data[0][0]:
                    l_num = int(data[0][0])
                db.close()
                logging.info('account {} crawl number is {}'.format(username.encode('utf-8'), l_num))
                # print time_period, num
            except Exception, e:
                # print Exception, e
                logging.warning('error, msg is {}'.format(str(e)), exc_info=True)
            if num >=  l_num: # 提供的数量大于 实际抓取的数量 还有额度可以抓
                return True
            else:
                return False


    def expired_user(self):
        ex_list = []
        try:
            day30 = datetime.date.today() + datetime.timedelta(days=50)
            sql = """select user_name from grapuser_info WHERE expire_time < '{}' and grap_source = '{}'""".format(day30, self.source)
            db = MySQLdb.connect(**self.sql_config)
            cur = db.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            for i in data:
                ex_list.append(i[0])
        except Exception, e:
            logging.error('try to find expired user fail', exc_info=True)
        return ex_list
    # def crawl_choose(self, time_period=0, num=0):
    #     """
    #     :param sc: 来源
    #     :param time_period: 时间长度
    #     :param num: 数字，
    #     :return: MySQL中的数字
    #     """
    #     l_51 = []
    #     res = None
    #
    #     # for i in self.all_account:
    #     #     if self.r.exists(i):
    #     #         if not self.redis_ismen('cookie_expired'):
    #     #             if time_period > 0 and num > 0:
    #     #                 l_num = self.sql_num(i.split('-')[1], num)
    #     #                 if num > l_num:   # 实际抓取的数量少于限额
    #     #                     l_51.append(i)
    #     #             else:
    #     #                 l_51.append(i)
    #     if len(l_51) > 0:
    #         res = random.choice(l_51)
    #     else:
    #         print 'no logined or no account left for 51job'
    #
    #     return res   # 返回的是redis key


    def uni_user(self, time_period=0, num=0, hour_num=0, day_num=0):
        """
        一个函数包装，下载，购买选择
        设定key参数表示在cookied 那里移除掉, 不需要判断有没有被多进程利用了
        :time_period 跟 num 是用户自己设定的频率，譬如 5分钟内抓 100 个那样子。
        day_num , 跟 hour_num 表示的是该账号 在一天内，或者 一小时内的抓取限额
        :return:
        """
        try:
            if self.option == 'down':
                self.all_account = self.sql_password3()
                if self.source == 'zl':
                    l = [i for i in self.all_account if i.startswith('cookiezl')]
                elif self.source == '51job':
                    l = [i for i in self.all_account if i.startswith('cookie51')]
                elif self.source == 'zjol':
                    l = [i for i in self.all_account if i.startswith('cookiecjol')]
                l2 = l
                # l2 = [i for i in l if not self.redis_ismen(i)]   # 确保没有作失效了的标记
                # flag = True
                # while flag:
                #     ii = random.choice(l2)
                #     l2.remove(ii)
                #     if self.sql_num(ii.split('_'), time_period, num):
                #         flag = False
                # return ii
                l3 = []
                l4 = []
                l5 = []
                for i2 in l2:
                    if self.sql_num(i2.split('_')[1], time_period, num):
                        l3.append(i2)
                if hour_num != 0:
                    for i3 in l3:
                        if self.sql_num(i3.split('_')[1], 3600, hour_num):
                            l4.append(i3)
                else:
                    l4 = l3
                if day_num != 0:
                    for i4 in l4:
                        if self.sql_num(i4.split('_')[1], 86400, day_num):
                            l5.append(i4)
                else:
                    l5 = l4
                return l5  # 返回的是一个符合条件的列表。 由脚本判断登录态

            else:
                username = None
                avail_list = self.cookie_choose(option=0)
                if len(avail_list) > 0:
                    f_flag = True
                    ex_list = self.expired_user()
                    ee_list = []
                    for i1 in ex_list:
                        if i1 in avail_list:
                            ee_list.append(i1)   # 两者交集
                    while f_flag:
                        if len(ee_list) > 0:
                            username = random.choice(ee_list)
                            ee_list.remove(username)
                            avail_list.remove(username)
                            ck_str = self.redis_ck_get(username)
                            self.num_update(source=self.source, un=username, ck_str=ck_str)
                            avail_num = int(self.avail_num(username))
                            if avail_num > 0:
                                # print 'Select user done and user is {}, avail num is {}'.format(username, avail_num)
                                logging.info('select expired user is {}, avail num is {}'.format(username, avail_num))
                                f_flag = False
                        else:
                            username = random.choice(avail_list)
                            avail_list.remove(username)
                            ck_str = self.redis_ck_get(username)
                            self.num_update(source=self.source, un=username, ck_str=ck_str)
                            avail_num = int(self.avail_num(username))
                            if avail_num > 0:
                                # print 'Select user done and user is {}, avail num is {}'.format(username, avail_num)
                                logging.info('select user is {} avail num is {}'.format(username, avail_num))
                                f_flag = False
                else:
                    logging.error('no avail login cookie file for {}'.format(self.source))
                    print '没有已经登陆的 {} cookie文件'.format(self.source)
                return username
        except Exception, e:
            logging.warning('error, msg is {}'.format(str(e)), exc_info=True)
            pass


if __name__ == '__main__':
    aa = Manage(source='cjol', option='down')
    # aa.account_all()
    # b = aa.uni_user()
    # print b
    b = aa.sql_password3()
    print b
