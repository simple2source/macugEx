# -*- coding:UTF-8 -*-


from BaseFetch import BaseFetch
import os, datetime, time, logging, urlparse, sys, cookielib, datetime
from common import *
from dbctrl import *
# import html5lib
reload(sys)
sys.setdefaultencoding('utf-8')
import traceback, sqlite3
from bs4 import BeautifulSoup
import urllib, urllib2, cookielib, bs4
from extract_seg_insert import ExtractSegInsert
from redispipe import *
import selectuser, liblogin
import shutil
import libaccount
import logging.config
import copy

class job51search(BaseFetch):
    def __init__(self, cookie_fpath='', task_fpath=''):
        BaseFetch.__init__(self)
        # if os.path.exists(cookie_fpath):
        #     self.load_cookie(cookie_fpath)
        # else:
        #     logging.debug('cookie file %s not exit.' % cookie_fpath)
        #     exit()
        self.account = libaccount.Manage(source='51job', option='down')
        self.host = r'ehire.51job.com'
        self.domain = '51job.com'
        self.module_name = '51search'
        self.init_path()
        self.login_wait = 300

        self.ctmname = ''
        self.username = ''
        self.password = ''
        self.ck_str = ''

        self.refer = ''
        self.headers = {
            'Host': self.host,
            'Origin': 'http://ehire.51job.com',
            'Referer': 'http://ehire.51job.com/Candidate/SearchResume.aspx',
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }

        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags = ['<td colspan="2" class="loginbar">',
                                '<input type="button" onclick="loginSubmit']

        self.resume_tags = ['<div id="divResume"><style>', '简历编号']
        self.login_success_tag = []

        # self.cookie_fpath = cookie_fpath
        self.taskfpath = task_fpath
        self.inuse_taskfpath = ''
        # self.years=['7C1', '7C2', '7C3', '7C4', '7C5', '7C6', '7C7', '7C8']
        self.gender = ['7C0', '7C1']
        self.degree = ['7C6', '7C7', '7C8']
        # self.degree = ['7C5', '7C6']
        self.area = ['7C040000', '7C030200', '7C010000', '7C020000']
        # self.area = ['7C040000', '7C030200']
        self.now_time = datetime.datetime.now()
        self.yes_time = self.now_time + datetime.timedelta(days=-2)
        self.seven_ago = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d')
        self.yester_time = self.yes_time.strftime('%Y-%m-%d')
        self.years_age_gender = []
        self.area_degree = []
        self.convert_dict = {'7C010000': '北京', '7C020000': '上海', '7C030200': '广州', '7C040000': '深圳',
                             '7C6': '本科', '7C7': '硕士', '7C8': 'MBA以上',
                             '7C3%7C3': '1-2年', '7C4%7C4': '2-3年', '7C5%7C5': '3-4年', '7C6%7C6': '5-7年',
                             '7C7%7C7': '8-9年', '7C8%7C8': '10年以上', '7C8%7C99': '10年以上'}
        # 用于记录执行号段任务的参数，起始/结束/当前
        self.start_num = 0
        self.end_num = 0
        self.current_num = self.start_num
        self.maxsleeptime = 5
        self.current_circle = 0

        self.rp = Rdsreport()
        # 下面几个参数是用来选择账号的
        self.time_period = 400
        self.time_num = 150  # 这个跟上面的可以限制选择账号的时候的抓取频率
        self.hour_num = 0
        self.day_num = 0
        self.switch_num = 30
        """
        :param time_period: 跟下面的额num 综合利用来限制频率的
        :param time_num:  同上， 可以设置短时间 抓取的个数，限制频率，60秒 5 个那样子
        :param hour_num: 限制一个小时的个数
        :param day_num: 限制一天的个数
        :return: 是否有可用账号，没有可用账号就循环等待，发
        """

        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'job51search.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')
        self.other_post_count = 3
        self.dynamic = 0

    def parse_cookie(self, fpath):
        '''功能描述：从cookie之中解析出来用户名，进而初始化企业名信息'''
        try:
            if os.path.exists(fpath):
                f = open(fpath)
                tmp_str = f.read()
                f.close()
                ck_dict = urlparse.parse_qs(tmp_str)
                if ck_dict.keys().count('UserName') == 1:
                    self.username = ck_dict['UserName'][0]
                    if job51_account_info.has_key(self.username):
                        self.ctmname = job51_account_info[self.username]
            return True
        except Exception, e:
            logging.debug('error msg is %s' % str(e))
            return False

    def load_task(self):
        '''功能描述：载入任务初始化相关参数'''
        try:
            logging.info('begin to load task from %s' % self.taskfpath)
            task_fname = os.path.split(self.taskfpath)[-1]
            self.inuse_taskfpath = os.path.join(self.task_inuse_dir, task_fname)
            move_file(self.taskfpath, self.inuse_taskfpath)
            f = open(self.inuse_taskfpath)
            file_str = f.read()
            f.close()
            file_str = file_str.replace('\r\n', '').replace('\n', '')
            tmp = file_str.split(';')[0]
            self.start_num = int(tmp.split(',')[0])
            self.end_num = int(tmp.split(',')[1])
            if self.end_num == self.start_num:
                self.end_num += 1
            self.current_num = int(file_str.split(';')[-1])
            if self.current_num < self.start_num:
                self.current_num = self.start_num
            logging.info('load task success from %s and occupy taskfile success' % self.taskfpath)
            return True
        except Exception, e:
            logging.debug('load task failed and error is %s' % str(e))
            return False

    def load_search_task(self):
        '''依据任务页面搜索关键字进行,载入初始化相关参数'''
        try:
            logging.info('begin to load search task from %s' % self.taskfpath)
            task_fname = os.path.split(self.taskfpath)[-1]
            self.inuse_taskfpath = os.path.join(self.task_inuse_dir, task_fname)
            move_file(self.taskfpath, self.inuse_taskfpath)
            f = open(self.inuse_taskfpath)
            file_str = f.read()
            f.close()
            # self.area_list = file_str.split(',')
            self.years = file_str.split("\r\n")[0].split(',')  # 读取本地task文件生成列表,当有多行的时候使用
            self.age = file_str.split("\r\n")[1].split(',')
            self.post_data = file_str.split("\r\n")[2]
            logging.info('load search_task success from %s' % self.taskfpath)
            return True
        except Exception, e:
            logging.debug('load search_task failed and error is %s' % str(e))
            return False

    def unload_task(self):
        '''功能描述：卸载任务，将任务放回原任务路径下'''
        try:
            logging.info('begin to unload task')
            try:
                shutil.move(self.inuse_taskfpath, self.taskfpath)
            except:
                shutil.copyfile(self.inuse_taskfpath, self.taskfpath)
                os.remove(self.inuse_taskfpath)
            return True
        except Exception, e:
            logging.debug('error msg is %s' % str(e))
            return False

    def get_task(self):
        '''功能描述：获取新的任务'''
        pass

    def isResume_chk(self, html):
        '''功能描述：检查返回内容是否为合格简历'''
        try:
            flag = -1
            if html:
                if html.find('此人简历保密') > -1:
                    flag = 2
                if html.find('屏蔽') > -1:
                    flag = 3
                if html.find('操作频繁') > -1:
                    flag = 4
                for item in self.need_login_tags:
                    if item and html.find(item) > -1:
                        flag = 0
                        break
                for sub in self.resume_tags:
                    if sub and html.find(sub) > -1:
                        flag = 1
                        break
            else:
                flag = -2
            if flag < 0:
                self.save_error_file(html)
            return flag
        except Exception, e:
            logging.debug('error msg is %s' % str(e))
            return -1

    def update_task(self):
        '''功能描述：更新任务，将执行进度写入到任务之中'''
        try:
            tmp_str = str(self.start_num) + ',' + str(self.end_num) + ';' + str(self.current_num)
            f = open(self.inuse_taskfpath, 'wb')
            f.write(tmp_str)
            f.close()
            if os.path.exists(self.taskfpath):
                f = open(self.taskfpath, 'wb')
                f.write(tmp_str)
                f.close()
            logging.info('success update taskfile %s' % self.inuse_taskfpath)
            return True
        except Exception, e:
            logging.debug('error msg is %s' % str(e))
            return False

    def fin_task(self):
        '''功能描述：任务完成之后的清理工作，将任务放至已完成路径'''
        try:
            task_fname = os.path.split(self.taskfpath)[-1]
            fin_fpath = os.path.join(self.task_fin_dir, task_fname)
            move_file(self.inuse_taskfpath, fin_fpath)
            txt_title = self.username + ' ' + 'task is complete' + ' ' + self.taskfpath
            txt_msg = self.module_name + ' 当前抓取页面任务路径:' + self.taskfpath
            # self.send_mails(txt_title, txt_msg, 0)
            logging.info('%s success crawl finish the task %s' % (self.username, self.taskfpath))
            return True
        except Exception, e:
            logging.debug('error msg is %s ' % str(e))
            return False

    def cookie_notice(self, notify_type=0):
        '''功能描述：cookie信息提醒，失效/生效'''
        try:
            if notify_type == 0:
                txt_title = self.module_name + ' cookie power off'
                txt_msg = self.module_name
                if self.ctmname:
                    txt_msg += ' 企业名称:' + self.ctmname
                if self.username:
                    txt_msg += ' 用户名:' + self.username
                txt_msg += ' cookie 已经失效，最近一次修改时间:' + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                    time.localtime(self.cookie_modtime))
                txt_msg += '<br> cookie path ' + self.cookie_fpath
                self.send_mails(txt_title, txt_msg, 0)
                cookie_old = self.cookie_fpath
                shutil.copyfile(cookie_old, cookie_old + '_old')
                logging.info('cookie power off and %s send notice_mail success' % self.module_name)
            elif notify_type == 1:
                txt_title = self.module_name + ' cookie login success'
                txt_msg = self.module_name
                if self.ctmname:
                    txt_msg += ' 企业名称:' + self.ctmname
                if self.username:
                    txt_msg += ' 用户名:' + self.username
                txt_msg += ' cookie 登录成功，cookie最新修改时间:' + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                        time.localtime(self.cookie_modtime))
                txt_msg += '<br> cookie path ' + self.cookie_fpath
                logging.info('cookie login success and %s send notice_mail success' % self.module_name)
            return True
        except Exception, e:
            logging.debug('error msg is %s' % str(e))
            return False

    def login(self):
        '''功能描述：判断登录状态处理登录过程，循环等待cookie更新直至登录cookie可用'''
        try:
            self.load_cookie(self.cookie_fpath)
            self.parse_cookie(self.cookie_fpath)
            flag = False
            if self.login_status_chk():
                flag = True
            else:
                l_count = 0
                while l_count <= 3:
                    try:
                        min_sleep = random.randint(10, 60)
                        time.sleep(min_sleep * 60)
                        l_count += 1
                        user_select = selectuser.Selcet_user('51job')
                        sql_res = user_select.sql_password(self.username)
                        self.password = sql_res[1]
                        self.ctmname = sql_res[0]
                        # try to login via liblogin
                        l_login = liblogin.Login51(cn=self.ctmname.encode('utf-8'), un=self.username, pw=self.password)
                        ck_str = l_login.login()
                        with open(self.cookie_fpath, 'w+') as f:
                            f.write(ck_str)
                        self.load_cookie(self.cookie_fpath)
                        if self.login_status_chk():
                            try:
                                logging.info("company name: {}, username: {} auto login success and count is {}, sleep time is {} min".format(self.ctmname, self.username, l_count, min_sleep))
                                # self.send_mails('{} auto login success'.format(self.module_name),
                                # "company name: {}, username: {} auto login success and count is {}, sleep time is {} min".format(self.ctmname, self.username, l_count, min_sleep))
                            except:
                                pass
                            flag = True
                        if flag:
                            break
                    except Exception, e:
                        logging.warning('auto try login error %s' % str(e))
                        pass
                if not flag:
                    # exit(0)
                    self.logout_at = datetime.datetime.now()
                    # flag = False
                    self.cookie_notice(0)
                    count = 0
                    while not flag:
                        try:
                            count += 1
                            logging.info('the login action will be executed after %ds ...' % self.login_wait)
                            time.sleep(self.login_wait)
                            if os.path.exists(self.cookie_fpath):  # 判断cookie文件是否存在
                                if os.path.getmtime(self.cookie_fpath) > self.cookie_modtime:
                                    self.load_cookie(self.cookie_fpath)
                                    self.parse_cookie(self.cookie_fpath)
                                    logging.info('cookie file updated at %s' % time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                             time.localtime()))
                                    logging.info('try to login at the count %d ' % count)
                                    if self.login_status_chk():
                                        flag = True
                                        self.cookie_notice(1)
                                        logging.info('success login at the count %d ' % count)
                                else:
                                    if count % 240 == 0:
                                        self.cookie_notice(0)
                                    read_modtime = time.strftime('%Y-%m-%d %H:%M:%S',
                                                                 time.localtime(os.path.getmtime(self.cookie_fpath)))
                                    record_modtime = time.strftime('%Y-%m-%d %H:%M:%S',
                                                                   time.localtime(self.cookie_modtime))
                                    logging.info('waite cookie update and modtime_read at %s ,modtime record at %s' % (
                                        read_modtime, record_modtime))
                            else:
                                logging.info('cookie file in %s is not exist... ' % self.cookie_fpath)
                                continue
                        except Exception, e:
                            logging.debug('single login error and msg is %s' % str(e))
                    self.login_at = datetime.datetime.now()
                    self.logout_at = None
            return flag
        except Exception, e:
            logging.debug('error msg is %s ' % str(e))
            return False

    def login_status_chk(self):
        '''功能描述：检查当前登录状态是否有效'''
        try:
            flag = False
            count = 0
            while count < 3:
                count += 1
                try:
                    chk_url = r'http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=10010'
                    self.rand_ua()
                    html = self.rand_get(chk_url)
                    if self.isResume_chk(html) > 0:
                        flag = True
                        break
                    time.sleep(5)
                except Exception, e:
                    logging.debug('single status check error and msg is %s' % str(e))
            return flag
        except Exception, e:
            logging.debug('error msg is %s ' % str(e))
            return False

    # def convert_display(self, convert=''):
    #      '''功能描述:将写入日志的信息转化为中文'''
    #      try:
    #          self.convert_dict = {'7C010000':'北京', '7C020000':'上海', '7C030200':'广州', '7C040000':'深圳', '7C5':'大专', '7C6':'本科', '7C7':'硕士', '7C8':'MBA以上'}
    #          return self.convert_dict[convert]
    #      except Exception,e:
    #          logging.debug('transfer is fail %s' % str(e))

    def get_cookie(self):    # 更改这里参数来选择账号
        try:
            flag = False
            # self.account = libaccount.Manage(source='51job', option='down')
            redis_key_list = self.account.uni_user(time_period=self.time_period, num=self.time_num, hour_num=self.hour_num, day_num=self.day_num)
            # print redis_key_list, 8888888888
            redis_key_list2 = copy.deepcopy(redis_key_list)
            for i in ['cookie51_shengde2', 'cookie51_shengde6', 'cookie51_shengde7', 'cookie51_shengde8']:
                if i in redis_key_list2:
                    redis_key_list.extend([i] * 2)
            if len(redis_key_list) > 0:
                while len(redis_key_list) > 0 and not flag:
                    redis_key = random.choice(redis_key_list)
                    redis_key_list.remove(redis_key)
                    self.username = redis_key.split('_')[1].encode('utf-8')
                    logging.info('51 get username is {}'.format(self.username))
                    # print(self.username), 99999999999
                    self.ck_str = self.account.redis_ck_get(self.username)
                    # print self.ck_str
                    self.headers['Cookie'] = self.ck_str
                    if self.login_status_chk():
                        flag = True
                        # print self.username * 100
                        logging.info('switching {} username {} success. '.format(self.module_name, self.username))
                    else:
                        sql_res = self.account.sql_password(self.username)
                        # print sql_res
                        self.account.redis_ck_ex(self.username)  # 更新该用户名的cookie失效时间
                        self.password = sql_res[1]
                        self.ctmname = sql_res[0].encode('utf-8')
                        # print self.password, self.username, self.ctmname
                        l_login = liblogin.Login51(cn=self.ctmname, un=self.username, pw=self.password)
                        self.ck_str = l_login.main(sleep=5)
                        self.headers['Cookie'] = self.ck_str
                        if self.login_status_chk():
                            self.account.redis_ck_set(self.username, self.ck_str)
                            logging.info('51job user {} auto login success'.format(self.username))
                            logging.info('switching {} username {} success. '.format(self.module_name, self.username))
                            flag = True
                return flag
            else:
                logging.critical('no account left for {}'.format(self.module_name))
                # 这里需要发邮件警告。
                return False

        except Exception, e:
            logging.critical('error msg is {}'.format(str(e)), exc_info=True)
            return False


    def login2(self):
        """主要是为了，没有可用账号的时候循环发邮件"""
        try:
            if self.login_status_chk():
                flag = True
            else:
                flag = self.get_cookie()
                print flag
                print self.ck_str
            if not flag:
                self.send_mails('222Warning, No account left for {}'.format(self.module_name), 'time is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                count = 0
                while not flag:
                    if self.login_status_chk():
                        flag = True
                        self.send_mails('33Now has account for {} '.format(self.module_name), 'time is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        logging.info('success get account at the count %d ' % count)
                    else:
                        self.logout_at = datetime.datetime.now()
                        flag= False
                        try:
                            count += 1
                            logging.info('the login action will be executed after %ds ...' % self.login_wait)
                            time.sleep(self.login_wait)
                            flag = self.get_cookie()  # 等5分钟
                            if count % 12  == 0:  # 一个小时还没可用账号就发邮件
                                self.send_mails('111Warning, No account left for {}'.format(self.module_name), 'time is {}, count is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), count)
                                logging.critical('no account left for {}'.format(self.module_name))
                        except Exception,e:
                            print Exception, e
                            logging.debug('single login error and msg is %s' % str(e))
            return flag
        except Exception, e:
            logging.error('login process error and error msg is {}'.format(str(e)), exc_info=True)
            return False


    # @property
    def run_search(self):
        ''' 功能描述：执行任务主工作入口函数,login会加载cookie '''
        try:
            switch_num = 0  # 用来计数的，切换cookie
            while True:
                self.get_cookie()
                self.login2()
                # self.load_cookie(self.cookie_fpath)
                # self.parse_cookie(self.cookie_fpath)
                self.load_search_task()
                print self.age
                age_int = int(self.age[0].replace('7C', ''))
                url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
                self.years_age_gender = []
                self.area_degree = []
                for m in self.years:
                    for n in self.age:
                        for g in self.gender:
                            self.years_age_gender.append(n + '-' + m + '-' + g)
                # print self.years_age_gender
                for area in self.area:
                    for deg in self.degree:
                        self.area_degree.append(area + '-' + deg)
                # print self.area_degree
                self.current_circle = query_age(age_int)
                print self.current_circle,'+++'
                self.current_circle += 1
                crawl_count = 0
                search_count = 0
                to_grab = 0
                start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')   # 以后修改
                total_crawl_resume = 0
                total_insert_resume = 0
                total_update_resume = 0
                page_error_count = 0
                hidWhere_1 = r'hidWhere=00%230%230%230%7C99%7C20151211%7C20151218%7C23%7C23%7C5%7C5%7C1_%'.replace(
                    '20151218', time.strftime('%Y%m%d', time.localtime())).replace('20151211', (
                    datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d'))
                hidWhere_2 = r'7C000000%7C040000%7C99%7C99%7C99%7C0000%7C6%7C6%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C000000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23'
                if '7C42' in self.age or '7C49' in self.age:
                    hidWhere_2 = r'7C000000%7C040000%7C99%7C99%7C99%7C0000%7C99%7C99%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C000000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0'
                for j in self.years_age_gender:
                    for v in self.area_degree:
                        end = False
                        search_count += 1
                        to_grab += 1
                        crawl_number = 0
                        crawl_es = 0
                        for n in range(1, 60):
                            if switch_num > self.switch_num:
                                logging.info('{} time to switch cookie'.format(self.module_name))
                                self.get_cookie()
                                switch_num = 0
                            seg_success_count = 0
                            sum_count = 0
                            seg_cover_ex = 0
                            seg_success_ex = 0
                            if end:
                                break
                            hidWhere = hidWhere_1.replace('7C23', j.split('-')[0]).replace('7C5%7C5',
                                                                                           j.split('-')[1]).replace(
                                '7C1_', j.split('-')[2]) + hidWhere_2.replace('7C040000', v.split('-')[0]).replace(
                                '7C6', v.split('-')[1])
                            # if self.other_post_count % 2 == 0:
                            #     with open('/data/fetch/task/51/task_comon.txt', 'r+') as other_f:
                            #         other_post_data = other_f.read()
                            #         post_data1 = other_post_data.replace('125', str(n)) + hidWhere
                            # else:
                            if self.dynamic == 0:
                                post_data1 = self.post_data.replace('125', str(n)) + hidWhere
                            else:
                                post_main = open('/data/fetch/task/51/post_main.txt', 'r+').read()
                                post_data1 = '__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=' + post_dynamic + post_main
                                post_data1 = post_data1.replace('125', str(n)) + hidWhere
                                print 'dynamic-----!!!!'
                                print post_data1
                            convert_area = self.convert_dict[v.split('-')[0]]
                            convert_degree = self.convert_dict[v.split('-')[1]]
                            convert_year = self.convert_dict[j.split('-')[1]]
                            t0 = time.time()
                            # job51html = open('job51.html','w+')
                            # html = self.url_post(url,post_data1)           # 获取网页对象
                            # job51html.write(html)
                            # job51html.close()
                            # soup = BeautifulSoup(open('job51.html'),'html.parser')     #解析出尾段对应的hiduserid

                            # 判断登录态是否失效,并重试,以及获取网页对象的简历链接列表
                            uplink = None
                            while not uplink:
                                try:
                                    self.rand_sleep()
                                    self.rand_ua()
                                    html = self.rand_post(url, post_data1)
                                    if html.find('id="Login_btnLoginCN"') > 0:
                                        self.login2()
                                    if html.find('抱歉，没有搜到您想找的简历') > 0:
                                        time.sleep(20)
                                        print 'sleep,-------,bad request'
                                        # record_error_condition(current_circle=self.current_circle, area=convert_area,
                                        #                        deg=convert_degree, age=j.split('-')[0][2:], gen=str(j.split('-')[2][2:]),
                                        #                        year=convert_year)
                                        logging.warning(
                                            'error condition request for %s page is %s' % (hidWhere, str(n)))
                                        end = True
                                        break
                                    soup = BeautifulSoup(html, 'html.parser')
                                    post_dynamic = soup.select('#__VIEWSTATE')[0]['value']
                                    post_dynamic = urllib.quote_plus(post_dynamic)
                                    self.dynamic += 1
                                    uplink = soup.select('.SearchR a')
                                    inbox = soup.select('td.inbox_td4')  # 解析出简历更新时间
                                    total_page = soup.select('strong')[1].get_text()
                                    exactly_page = soup.select('strong')[1].get_text().split('/')[0]
                                    total_page_count = soup.select('strong')[1].get_text().split('/')[1]
                                    total_search_count = soup.select('strong')[0].get_text()
                                    if int(total_search_count) > 2500:
                                        page_error_count += 1
                                    page_update_time = 0
                                    for p in inbox:
                                        try:
                                            update_time = p.get_text()
                                            if update_time.find('2016') == 0:
                                                page_update_time = update_time
                                                break
                                        except Exception, e:
                                            logging.debug('erro msg is page_update_time %s ' % str(e))
                                    if page_update_time == 0:
                                        page_update_time = datetime.datetime.now().strftime('%Y-%m-%d')
                                    if n >= int(total_page_count):
                                        end = True
                                        break
                                except Exception, e:
                                    pass
                                    print traceback.format_exc()
                                    logging.error('51job_latest error work_area: %s  page: %s request is %s ...' % (
                                        str(v), str(n), str(e)))
                            # 解析出html格式
                            if uplink:
                                resume = {'id': '', 'age': '', 'work_year': '', 'degree': '', 'resume_update_time': '',
                                          'domicile': '', 'sex': ''}
                                for i in uplink:
                                    sum_count += 1
                                    urllink = r'http://ehire.51job.com/' + i['href']
                                    x = urlparse.urlparse(urllink)
                                    x = urlparse.parse_qs(x.query, True)
                                    x = x['hidUserID'][0]
                                    # x = x['http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID'][0]
                                    self.current_num = x
                                    print x, urllink
                                    prefixid = 'wu_' + str(x)
                                    addtime = page_update_time + ' 00:00:00'
                                    r = self.rp
                                    # if self.resume_exist_chk(x):
                                    #     logging.info('resume %s already exist.' % str(x))
                                    if r.rcheck(prefixid, addtime, 1):
                                    #     flag = True
                                    #     else:
                                    #         flag = False
                                    # else:
                                    #     flag = True
                                    #     r.rcheck(prefixid, addtime, 1)
                                    # if flag:
                                        req_count = 0
                                        while req_count < 3:
                                            req_count += 1
                                            try:
                                                logging.info('begin to get resume %s from Internet' % str(x))
                                                self.rand_ua()
                                                urlhtml = self.rand_get(urllink)
                                                isResume = self.isResume_chk(urlhtml)
                                                if isResume == -2:
                                                    req_count = 0
                                                elif isResume == -1:
                                                    req_count = 3
                                                elif isResume == 0:
                                                    self.login2()
                                                    req_count = 0
                                                elif isResume == 1:
                                                    switch_num += 1
                                                    if self.save_resume(str(x), urlhtml):
                                                        seg_success_count += 1
                                                        total_crawl_resume += 1
                                                        crawl_number += 1
                                                        data_total_add(self.module_name)
                                                        r.tranredis('51search', 1, ext1=self.username, ext2='ok',
                                                                    ext3='')
                                                        add_total_num(os.path.split(self.taskfpath)[-1])
                                                        resume = ExtractSegInsert.extract_51(html_file='', content=urlhtml, output_dir='')
                                                        try:
                                                            es_redis = r.es_check(prefixid)
                                                            if es_redis == 0:
                                                                data_back = ExtractSegInsert.fetch_do123(urlhtml,
                                                                                                         '51job', 1)
                                                                crawl_es += 1
                                                            elif es_redis == 1:
                                                                data_back = ExtractSegInsert.fetch_do123(urlhtml,
                                                                                                         '51job', -1)
                                                                crawl_es += 1
                                                            resume = data_back[0]
                                                            ex_result = data_back[1]
                                                            print ex_result, resume
                                                            if ex_result == 1:
                                                                r.tranredis('51search_seg', 1, ext1='insert', ext2='ok')
                                                                r.es_add(prefixid, addtime, 1)
                                                                seg_success_ex += 1
                                                                total_insert_resume +=1
                                                            elif ex_result == -1:
                                                                r.tranredis('51search_seg', 1, ext1='update', ext2='ok')
                                                                r.es_add(prefixid, addtime, 1)
                                                                seg_cover_ex += 1
                                                                total_update_resume += 1
                                                            elif ex_result == -4:
                                                                r.tranredis('51search_seg', 1, ext1='update',
                                                                            ext2='search_err')
                                                                r.es_add(prefixid, addtime, 1)
                                                            elif ex_result == 0:
                                                                r.tranredis('51search_seg', 1, ext1='insert',
                                                                            ext2='not_insert')
                                                                r.es_add(prefixid, addtime, 0)
                                                            elif ex_result == -2:
                                                                r.tranredis('51search_seg', 1, ext1='',
                                                                            ext2='parse_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                                error_path = os.path.join('error/51search',
                                                                                          str(x) + '.html')
                                                                with open(error_path, 'w+') as f:
                                                                    f.write(urlhtml)
                                                            elif ex_result == -3:
                                                                r.tranredis('51search_seg', 1, ext1='',
                                                                            ext2='source_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                            elif ex_result == -5:
                                                                r.tranredis('51search_seg', 1, ext1='',
                                                                            ext2='operate_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                        except Exception, e:
                                                            print traceback.format_exc()
                                                            logging.warning(
                                                                '51job resume_id %s extractseginsert fail error msg is %s' % (
                                                                    str(x), e))
                                                    else:
                                                        pass
                                                    break
                                                elif isResume == 2:
                                                    logging.info('resume_id %s is secret resume.' % str(x))
                                                    r.tranredis('51search', 1, ext1=self.username, ext2='secret')
                                                    break
                                                elif isResume == 3:
                                                    logging.info('resume_id %s is removed by system.' % str(x))
                                                    r.tranredis('51search', 1, ext1=self.username, ext2='remove')
                                                    print url
                                                    break
                                                elif isResume == 4:
                                                    logging.info('too more busy action and have a rest')
                                                    r.tranredis('51search', 1, ext1=self.username, ext2='busy')
                                                    time.sleep(20 * 60)
                                                    break
                                            except Exception, e:
                                                logging.debug('get %s resume error and msg is %s' % (str(x), str(e)))
                                        self.rand_sleep()
                #                 # date_list = []
                #                 # for k in inbox:
                #                 #     update_time = k.string
                #                 #     if isinstance(update_time,basestring) and update_time.find('2016') == 0:
                #                 #         date_list.append(update_time)
                #                 #     else:
                #                 #         continue
                #                 # if date_list[-1].find('2016') == 0 and self.yester_time > date_list[-1]:             # 判断页面日期大于2天之前退出循环
                #                 #     end = True
                #                 #     logging.info('break current loop %s' % time.asctime())
                                percent = 0
                                percent = int((float(seg_success_count) / sum_count) * 100)
                                begin_num, seg_end = 0, 0
                                data_seg_record(self.module_name, seg_success_count, [begin_num, seg_end, percent])
                                t1 = time.time() - t0
                                crawl_count += 1
                                logging.info(
                                    '<-----+++ 1,%s +++++,crawl 已经抓取页面数:%s ,take_time=%d s,current_page=%s,success get %d unique resumes and the rate is %d%% ||--->入库新增:%s 入库覆盖:%s ||-->2,crawl_condition:area=%s,degree=%s, work_year=%s, age=%s, gender=%s ||--->3,条件数:%s--- crawl post_data: %s ||*****' % (
                                        self.username, str(crawl_count), t1, str(n), seg_success_count, percent,
                                        str(seg_success_ex), str(seg_cover_ex), convert_area, convert_degree, convert_year,
                                        j.split('-')[0][2:], j.split('-')[2][2:], str(search_count), hidWhere))
                                print start_time
                                add_log_sqlite(user=self.username, area=convert_area, deg=convert_degree,
                                               age=j.split('-')[0][2:], gen=str(j.split('-')[2][2:]), year=convert_year,
                                               current_page=n, exatly_page=int(exactly_page), sum_page=int(total_page_count),
                                               resume_sum=int(total_search_count), p_time=str(t1), seg_count=seg_success_count,
                                               resume_insert=seg_success_ex, resume_update=seg_cover_ex,
                                               current_circle=self.current_circle,start_time=start_time,total_resume=total_crawl_resume,total_insert=total_insert_resume,total_update=total_update_resume,condition_count=to_grab,page_error_count=page_error_count)
                                try:
                                    logging.info(
                                        '--####4,%s ####-- crawl Excatly 页面简历总数=%s, page_count=%s,||--->latest_id=%s,resume_id=%s,gender=%s,age=%s, work_year=%s, area=%s, degree=%s,resume_update_time=%s ||##--->' % (
                                            self.username, total_search_count, total_page, str(x), resume['id'],
                                            resume['sex'], resume['age'], resume['work_year'], resume['domicile'],
                                            resume['degree'], resume['resume_update_time']))
                                except Exception, e:
                                    logging.warning('error 5,%s crawl transfer is fail %s' % (self.username, str(e)))

                self.fin_task()
                self.other_post_count += 1
                fin_fetch_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open('db/' + self.age[0] + '.log', 'a+') as fin_fetch:
                    fin_fetch.write(start_time + ' - ' + fin_fetch_time + ' ' + self.taskfpath + '---' + '\n')
                print self.username + 'will sleep' + '----------'
                time.sleep(2000 * 2)
        except Exception, e:
            print traceback.format_exc()
            logging.debug('error msg is %s' % str(e))
            return False


def add_log_sqlite(user='', area='', deg='', age='', gen='', year='', current_page=0, exatly_page=0, sum_page=0, resume_sum=0, p_time='',
                   seg_count=0, resume_insert=0, resume_update=0, current_circle=0,start_time='', total_resume=0, total_insert=0,total_update=0,condition_count=0,page_error_count=0):
     try:
        conn = sqlite3.connect(os.path.join(database_root,'search_log.db'))
        conn.text_factory = str
        cur=conn.cursor()
        print user, area, deg, age, gen, year, current_page, exatly_page, sum_page, resume_sum, p_time, seg_count, resume_insert, resume_update,\
                current_circle,start_time,total_resume,total_insert,total_update,condition_count,page_error_count
        cur.execute( '''INSERT INTO search_log (user,area,deg,age,gen,year,current_page,
            exatly_page, sum_page, resume_sum, p_time, seg_count, resume_insert, resume_update,
                current_circle,start_time, total_resume,total_insert,total_update,condition_count,page_error_count,at_time) VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime("now", "localtime"))''', (
                user, area, deg, age, gen, year, current_page, exatly_page, sum_page, resume_sum, p_time, seg_count, resume_insert, resume_update,
                current_circle,start_time,total_resume,total_insert,total_update,condition_count,page_error_count))
        # conn.execute(
        #     '''INSERT INTO search_log (user,area,deg,age,gen,year,current_page,
        #     exatly_page, sum_page, resume_sum, p_time, seg_count, resume_insert, resume_update,
        #         current_circle,start_time, total_resume,total_insert,total_update,condition_count,at_time) VALUES
        #         ('{}','{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}', '{}', '{}','{}','{}',datetime("now", "localtime"))'''.format(
        #         user, area, deg, age, gen, year, current_page, exatly_page, sum_page, resume_sum, p_time, seg_count, resume_insert, resume_update,
        #         current_circle,start_time,total_resume,total_insert,total_update,condition_count))
        conn.commit()
        conn.close()
        logging.info('%s record sqlite3 success ' % age)
     except Exception, e:
        print traceback.format_exc(), e

def record_error_condition(current_circle=0,
                           area='', deg='', age='', gen='', year=''):
    '''记录异常的请求条件'''
    try:
        conn=sqlite3.connect('/data/fetch/database/search_log.db')
        conn.text_factory = str
        cur =conn.cursor()
        cur.execute('''INSERT INTO error_condition (current_circle,
        area, deg, age, gen, year,at_time) VALUES
         (?,?,?,?,?,?,datetime("now", "localtime"))''', (current_circle, area, deg, age, gen, year))
        conn.commit()
        conn.close()
        print 'error_condition: --', area, deg, age, gen, year
    except Exception, e:
        print traceback.format_exc(), e

def query_age(age_int):
    try:
        conn = sqlite3.connect(os.path.join(database_root, 'search_log.db'))
        result = conn.execute('select current_circle from search_log where '
                          'age=%d order by id desc limit 1' % age_int).fetchall()[0][0]
        return result
    except Exception, e:
        print traceback.format_exc(),e

def add_total_num(fname=''):
    '''功能描述：采用文件方式记录总数'''
    try:
        fpath = '51job_success' + fname
        org_num = 0
        if os.path.exists(fpath):
            f = open(fpath, 'rb')
            org_num = int(f.read())
            f.close()
        f = open(fpath, 'wb')
        f.write(str(org_num + 1))
        f.close()
        logging.info('51job success get %d resumes now' % (org_num + 1))
        return True
    except Exception, e:
        logging.debug('error msg is %s' % str(e))
        return False


if __name__ == '__main__':
    print 'test...'
    ck_path = r'C:\python space\fetch\cookie\51.txt'
    tk_path = r'C:\python space\fetch\task\task.txt'
    a = job51search(ck_path, tk_path)
    a.run_work
