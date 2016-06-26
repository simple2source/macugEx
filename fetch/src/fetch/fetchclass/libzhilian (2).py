#-*- coding:UTF-8 -*-

from BaseFetch import BaseFetch
import os,datetime,time,logging,urlparse,sys,cookielib,traceback
from common import *
from dbctrl import *
from bs4 import BeautifulSoup
import urllib,urllib2
from extract_seg_insert import ExtractSegInsert
from redispipe import *
import libaccount
import logging.config
import liblogin
from getProxy import *
import subprocess

class zhilianfetch(BaseFetch):
    def __init__(self,cookie_fpath='',task_fpath=''):
        BaseFetch.__init__(self)
        # if os.path.exists(cookie_fpath):
        #     self.load_cookie(cookie_fpath)
        # else:
        #     logging.debug('cookie file %s not exit.' % cookie_fpath)
        #     exit()

        self.account = libaccount.Manage(source='zhilian', option='down')
        self.host=r'rd.zhaopin.com'
        self.domain='zhaopin.com'
        self.module_name='zhilian'
        self.init_path()
        self .login_wait=300

        self.ctmname=''
        self.username=''
        self.password=''
        self.refer=''
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Origin': 'http://rdsearch.zhaopin.com',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer':'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=java&SF_1_1_4=2%2C99&SF_1_1_18=765&orderBy=DATE_MODIFIED,1&pageSize=60&SF_1_1_27=0&exclude=1',
        }

        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags=['name="login"',
                              '<input id="LoginName" name="UserID" type="text" value="" placeholder="请输入用户名" />']
        self.resume_tags=['个人信息', '求职意向']
        self.login_success_tag=[]

        self.cookie_fpath=cookie_fpath
        self.taskfpath=task_fpath
        self.inuse_taskfpath=''

        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
        self.maxsleeptime = 6
        self.circle_count = 0
        # self.skill_list = ['php','c%2B%2B','javascript','html5','%E5%AE%89%E5%8D%93','android','ios','java','%E8%AE%BE%E8%AE%A1','%E4%BA%A7%E5%93%81','%E8%81%8C%E8%83%BD','%E5%B8%82%E5%9C%BA']
        self.area_list=['530','538','763','765']
        # self.area_list=['530','538','763']
        # self.years=['1%2C1','2%2C2','3%2C3','4%2C4','5%2C5','6%2C6','7%27','8%2C8','9%2C9','10%2C99']
        # self.years=['1%2C1','2%2C2']
        self.now_time = datetime.datetime.now()
        self.yes_time = self.now_time + datetime.timedelta(days=-3)
        self.yester_time = self.yes_time.strftime('%Y-%m-%d').replace('20','')

        self.rp = Rdsreport()
        # 下面几个参数是用来选择账号的
        self.time_period = 400
        self.time_num = 150  # 这个跟上面的可以限制选择账号的时候的抓取频率
        self.hour_num = 0
        self.day_num = 0
        self.switch_num = 30
        """
        :param time_period: 跟下面的额num 综合利用来限制频率的
        :param time_num:  同上， 可以设置短时间 抓取的个数，限制频率，1分钟 5 个那样子
        :param hour_num: 限制一个小时的个数
        :param day_num: 限制一天的个数
        :return: 是否有可用账号，没有可用账号就循环等待，发
        """

        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'zhiliansearch.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')

        self.address = ''

    def load_task(self):
        '''功能描述：载入任务初始化相关参数'''
        try:
            logging.info('begin to load task from %s' % self.taskfpath)
            task_fname=os.path.split(self.taskfpath)[-1]
            self.inuse_taskfpath=os.path.join(self.task_inuse_dir,task_fname)
            move_file(self.taskfpath,self.inuse_taskfpath)
            f=open(self.inuse_taskfpath)
            file_str=f.read()
            f.close()
            file_str = file_str.replace('\r\n','').replace('\n','')
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
        except Exception,e:
            logging.debug('load task failed and error is %s' % str(e))
            return False

    def load_search_task(self):
        '''依据任务页面搜索关键字进行,载入初始化相关参数'''
        try:
            logging.info('begin to load search task from %s' % self.taskfpath)
            task_fname = os.path.split(self.taskfpath)[-1]
            self.inuse_taskfpath = os.path.join(self.task_inuse_dir,task_fname)
            move_file(self.taskfpath,self.inuse_taskfpath)
            f=open(self.inuse_taskfpath)
            file_str = f.read()
            f.close()
            if self.taskfpath.find('zone') >0:
                self.username = 'Vinson_2015'
            elif self.taskfpath.find('skill') >0:
                self.username = 'hh10001210'
            elif self.taskfpath.find('industry') >0:
                self.username = '9910001210'
            elif self.taskfpath.find('age') >0:
                self.username = 'gg10001210'
            elif self.taskfpath.find('yrs') >0:
                self.username = '1010001210'

            self.search_list = file_str.split("\n")[0].split(',')     #读取本地task文件生成列表
            # self.skill_list = file_str.replace('\n','').split(',')
            logging.info('load search_task success from %s' % self.taskfpath)
            return True
        except Exception,e:
            logging.debug('load search_task failed and error is %s' % str(e))
            return False

    def unload_task(self):
        '''功能描述：卸载任务，将任务放回原任务路径下'''
        try:
            logging.info('begin to unload task')
            try:
                shutil.move(self.inuse_taskfpath,self.taskfpath)
            except:
                shutil.copyfile(self.inuse_taskfpath,self.taskfpath)
                os.remove(self.inuse_taskfpath)
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False

    def get_task(self):
        '''功能描述：获取新的任务'''
        pass

    def isResume_chk(self,html):
        '''功能描述：检查返回内容是否为合格简历'''
        try:
            flag = -1
            if html:
                if html.find('无法查看') > -1:
                    flag = 2
                    self.save_error_file(html)
                if html.find('该求职上传了附件简历,查看联系方式后可下载') > -1:
                    flag = 3
                if html.find('查看的简历数量已经超过限制') > -1:
                    flag = 4
                    self.save_error_file(html)
                if html.find('输入验证码才能继续后续的操作') > -1:
                    flag = 6
                for sub in self.resume_tags:
                    if sub and html.find(sub) > -1:
                        flag =1
                        break
            else:
                flag = -2
            if flag < 0 :
                self.save_error_file(html)
            return flag
        except Exception,e:
            logging.debug('error msg is %s'% str(e))
            return -1

    def update_task(self):
        '''功能描述：更新任务，将执行进度写入到任务之中'''
        try:
            tmp_str =str(self.start_num)+','+str(self.end_num)+';'+str(self.current_num)
            f=open(self.inuse_taskfpath,'wb')
            f.write(tmp_str)
            f.close()
            if os.path.exists(self.taskfpath):
                f=open(self.taskfpath,'wb')
                f.write(tmp_str)
                f.close()
            logging.info('success update taskfile %s' % self.inuse_taskfpath)
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False

    def fin_task(self):
        '''功能描述：任务完成之后的清理工作，将任务放至已完成路径'''
        try:
            task_fname=os.path.split(self.taskfpath)[-1]
            fpath = 'zhilian_success' + task_fname
            f = open(fpath,'rb')
            f_success = f.read()
            f.close()
            self.circle_count +=1
            fin_fpath=os.path.join(self.task_fin_dir,task_fname)
            move_file(self.inuse_taskfpath, fin_fpath)
            # txt_title = self.module_name + ' 当前单次循环抓取完成' + self.taskfpath
            # txt_msg = self.module_name+' 当前抓取页面任务路径:'+self.taskfpath +'<br>当前抓取任务完成总计:'+f_success+'<br>当前抓取循环次数为:'+str(self.circle_count)
            # self.send_mails(txt_title,txt_msg,0)
            logging.info('%s swoop success finish the task %s' % (self.username, self.taskfpath))
            return True
        except Exception,e:
            logging.debug('error msg is %s ' % str(e))
            return False

    def cookie_notice(self,notify_type=0):
        '''功能描述：cookie信息提醒，失效/生效'''
        try:
            if notify_type == 0:
                txt_title = self.module_name+' cookie power off'
                txt_msg=self.module_name+ ' cookie 已经失效，最近一次修改时间:'+ time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.cookie_modtime))
                self.send_mails(txt_title,txt_msg,0)
                logging.info('cookie power off and %s send notice_mail success' % self.module_name)
            elif notify_type == 1:
                txt_title = self.module_name+' cookie login success'
                txt_msg=self.module_name+ ' cookie 登录成功，cookie最新修改时间:'+ time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.cookie_modtime))
                self.send_mails(txt_title,txt_msg,0)
                logging.info('cookie login success and %s send notice_mail success' % self.module_name)
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False

    def login(self):
        '''功能描述：判断登录状态处理登录过程，循环等待cookie更新直至登录cookie可用'''
        try:
            self.load_cookie(self.cookie_fpath)
            flag = False
            if self.login_status_chk():
                flag = True
            else:
                #exit(0)
                self.logout_at = datetime.datetime.now()
                flag= False
                self.cookie_notice(0)
                count = 0
                while not flag:
                    try:
                        count += 1
                        logging.info('the login action will be executed after %ds ...' % self.login_wait)
                        time.sleep(self.login_wait)
                        if os.path.getmtime(self.cookie_fpath) > self.cookie_modtime:
                            self.load_cookie(self.cookie_fpath)
                            logging.info('cookie file updated at %s' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
                            logging.info('try to login at the count %d ' % count)
                            if self.login_status_chk():
                                flag =True
                                self.cookie_notice(1)
                                logging.info('success login at the count %d ' % count)
                        else:
                            if count % 24 == 0:
                                self.cookie_notice(0)
                            read_modtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(self.cookie_fpath)))
                            record_modtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.cookie_modtime))
                            logging.info('waite cookie update and modtime_read at %s ,modtime record at %s' % (read_modtime,record_modtime))
                    except Exception,e:
                        logging.debug('single login error and msg is %s' % str(e))
                self.login_at=datetime.datetime.now()
                self.logout_at=None
            return flag
        except Exception,e:
            logging.debug('error msg is %s ' % str(e))
            return False

    def login_status_chk(self):
        '''功能描述：检查当前登录状态是否有效'''
        try:
            flag = False
            count =0
            while count < 3:
                count +=1
                try:
                    chk_url = r'http://rdsearch.zhaopin.com/Home/'
                    html = self.url_get(chk_url)
                    if self.isResume_chk(html) > 0:
                        flag = True
                        break
                    time.sleep(5)
                except Exception,e:
                    logging.debug('single status check error and msg is %s' % str(e))

            return flag
        except Exception,e:
            logging.debug('error msg is %s ' % str(e))
            return False

    def test_proxy(self):
        try:
            flag = False
            while not flag:
                run_proxy = UseProxy()
                ip_list = run_proxy.random_ip()
                seg = 0
                url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=php&orderBy=DATE_MODIFIED,1&pageSize=60&SF_1_1_27=0&exclude=1'
                for ip in ip_list:
                    seg += 1
                    proxy_html = proxy_url_get(url, ip,headers=self.headers,timeout=2)
                    print ip,'.........'
                    if proxy_html:
                        if proxy_html.find('您搜索的是') > 0 and proxy_html.find('php') > 0:
                            self.address = ip
                            print '-----correct',self.address
                            flag = True
                            break
                if seg == len(ip_list):
                    print '-----new fetch proxy'
                    run_proxy.get_proxy()

            return True
        except Exception, e:
            print e, traceback.format_exc()

    def update_proxy(self, ip):
        try:
            url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=php&orderBy=DATE_MODIFIED,1&pageSize=60&SF_1_1_27=0&exclude=1'
            proxy_html = self.proxy_url_get(url, ip)
            if proxy_html:
                logging.info('proxy ip is useful %s' % self.address)
            else:
                self.test_proxy()
                logging.info('Get proxy IP again %s' % self.address)

            return True
        except Exception, e:
            print e, traceback.format_exc()



    def get_cookie1(self):   # 这个是用来挑搜索账号的，libaccount 那边就不另外搞了....不判断登录态了
        try:
            user_list = [
                '201510302',
                '201510303',
                '201510304',
                '201510305',
                'br620151102',
                'br720151102',
                'br820151102',
                'br920151102',
                'vinson5001104',
                'h24',
                'ffy65700282v',
                'peter10001210',
                'two10001210',

                'gg10001210',
                'hh10001210',
                '9910001210',
                '1010001210',
                '350bj1217',
                '350bj1216',
                'Ju2yuan',
                'jake5041225',
                'shengfeng1',
                'shchj']

            self.username = random.choice(user_list)
            self.ck_str = self.account.redis_ck_get(self.username)
            print self.ck_str
            self.headers['Cookie'] = self.ck_str
            # flag = False
            # while len(user_list) > 0 and not flag:
            #     self.username = random.choice(user_list)vi
            #     user_list.remove(self.username)
            #     self.ck_str = self.account.redis_ck_get(self.username)
            #     print self.ck_str
            #     self.headers['Cookie'] = self.ck_str
            #     l_login = liblogin.LoginZL(cn=self.ctmname, un=self.username, pw=self.password)
            #     if l_login.check_login():
            #         flag = True
        except:
            return False

    def get_cookie(self):    # 更改这里参数来选择账号
        try:
            flag = False
            redis_key_list = self.account.uni_user(time_period=self.time_period, num=self.time_num, hour_num=self.hour_num, day_num=self.day_num)
            print redis_key_list, 8888888888
            if len(redis_key_list) > 0:
                while len(redis_key_list) > 0 and not flag:
                    redis_key = random.choice(redis_key_list)
                    redis_key_list.remove(redis_key)
                    self.username = redis_key.split('_')[1]
                    print(self.username), 99999999999
                    self.ck_str = self.account.redis_ck_get(self.username)
                    print self.ck_str
                    self.headers['Cookie'] = self.ck_str
                    l_login = liblogin.LoginZL(cn=self.ctmname, un=self.username, pw=self.password)
                    if l_login.check_login():
                        flag = True
                        logging.info('switching {} username {} success. '.format(self.module_name, self.username))
                    else:
                        sql_res = self.account.sql_password(self.username)
                        print sql_res
                        self.account.redis_ck_ex(self.username)  # 更新该用户名的cookie失效时间
                        self.password = sql_res[1]
                        self.ctmname = sql_res[0]

                        self.ck_str = l_login.main()
                        self.headers['Cookie'] = self.ck_str
                        if self.login_status_chk():
                            self.account.redis_ck_set(self.username, self.ck_str)
                            logging.info('zhilian user {} auto login success'.format(self.username))
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
                self.send_mails('Warning, No account left for {}'.format(self.module_name), 'time is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            count = 0
            while not flag:
                if self.login_status_chk():
                    flag = True
                    self.send_mails('Now has account for {} '.format(self.module_name), 'time is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
                            self.send_mails('Warning, No account left for {}'.format(self.module_name), 'time is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                            logging.critical('no account left for {}'.format(self.module_name))
                    except Exception,e:
                        logging.debug('single login error and msg is %s' % str(e))
                return flag
        except Exception, e:
            logging.error('login process error and error msg is {}'.format(str(e)), exc_info=True)
            return False

    def run_search(self):
        '''功能描述：执行任务主工作入口函数'''
        try:
            switch_num = 0
            while True:
                # self.load_cookie(self.cookie_fpath)
                # self.parse_cookie(self.cookie_fpath)
                self.get_cookie()
                self.load_search_task()
                os.environ['http_proxy']='http://183.131.144.102:8081'
                subprocess.Popen('export',close_fds=True, shell=True,env=os.environ)
                print self.search_list,self.username
                # if len(self.area_list)==5:                  # 目前依据地区任务列表长度来进行抓取,后续直接可以将地区写死,将技能\行业\岗位作为本地task加载进来
                #     self.years = self.skill_list
                # if self.test_proxy():
                #     print self.address,'++++++'
                # else:
                #     logging.error('proxy get fail')
                #     sys.exit()
                for m in self.area_list:
                    for l in self.search_list:
                        end = False
                        for n in range(1, 67):
                            if end:
                                break
                            seg_success_count = 0
                            sum_count = 0
                            seg_success_ex = 0
                            seg_cover_ex = 0
                            self.rand_sleep()
                            if len(self.search_list) == 11:
                                # url = url.replace('3%2C3',i[1]).replace('16',str(n)).replace('763',i[0])
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_4=3%2C3&SF_1_1_18=763&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=16'
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_7=2%2C9&SF_1_1_4=3%2C3&SF_1_1_18=763&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&exclude=1&pageIndex=16'
                                url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_7=2%2C9&SF_1_1_4=3%2C3&SF_1_1_18=763&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=133'
                                url = url.replace('SF_1_1_4=3%2C3&', l).replace('133', str(n)).replace('763', m)
                            elif len(self.search_list) == 12:
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=php&SF_1_1_7=2%2C9&SF_1_1_18=530&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&exclude=1&pageIndex=16'
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=php&SF_1_1_18=530&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=16'
                                url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=php&SF_1_1_7=2%2C9&SF_1_1_18=530&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=1333'
                                url = url.replace('1333', str(n)).replace('530', m).replace('php', l)
                            elif len(self.search_list) == 10:
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_7=2%2C9&SF_1_1_18=538&SF_1_1_8=20%2C20&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&exclude=1&pageIndex=16'
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_18=538&SF_1_1_8=20%2C20&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=16'
                                url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_7=2%2C9&SF_1_1_18=538&SF_1_1_8=20%2C20&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=133'
                                url = url.replace('133',str(n)).replace('538',m).replace('20%2C20&',l)
                            elif len(self.search_list) == 7:
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_3=210500&SF_1_1_7=2%2C9&SF_1_1_18=538&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&exclude=1&pageIndex=17'
                                # url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_18=538&SF_1_1_3=210500&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=17'
                                url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_3=210500&SF_1_1_7=2%2C9&SF_1_1_18=538&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=177'
                                url = url.replace('177', str(n)).replace('538', m).replace('210500', l)
                            elif len(self.search_list) == 6:
                                url = r'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_7=2%2C9&SF_1_1_4=3%2C3&SF_1_1_18=763&SF_1_1_27=0&orderBy=DATE_MODIFIED%2C1&pageSize=60&exclude=1&pageIndex=177'
                                url = url.replace('SF_1_1_4=3%2C3&', l).replace('177', str(n)).replace('763', m)
                            self.get_cookie1()   # 访问搜索页面的时候切换到那4个账号
                            html = self.url_get(url)
#                             html = self.proxy_url_get(url, self.address)
#                             while not html:
#                                 print 'first ---- proxy'
#                                 if self.test_proxy():
#                                     html = self.proxy_url_get(url, self.address)
                            # html = self.url_get(url)
                            # html = self.proxy_url_get(url, self.address)                 #代理暂时不启用
                            # while not html:
                            #     print 'first ---- proxy'
                            #     if self.test_proxy():
                            #         html = self.proxy_url_get(url, self.address)
                            if html.find('name="login"') > 0:
                                txt_title = self.username + '' + 'cookie is unusable'
                                txt_msg = self.module_name + self.taskfpath + '<br>' + 'is fail'
                                self.send_mails(txt_title, txt_msg, 0)
                                time.sleep(5000*2)
                            soup = BeautifulSoup(html, 'html.parser')
                            uplink = soup.select('.first-weight a')
                            inbox = soup.select("td")
                            resume ={'id': '', 'age': '', 'work_year': '', 'degree': '', 'resume_update_time': '', 'domicile': '', 'sex': ''}
                            if not inbox:
                                txt_title = self.module_name+'error request url'
                                txt_msg = self.module_name+'<br>'+'当前抓取页面错误的地址为:'+url
                                # self.send_mails(txt_title, txt_msg, 0)
                                logging.info('%s the wrong search page is %s' % (self.username, url))
                                time.sleep(20)
                                break
                            total_page = soup.select('#rd-resumelist-pageNum')[0].get_text()
                            if n == soup.select('#rd-resumelist-pageNum')[0].get_text().split('/')[1]:
                                end = True
                            page_update_time = 0
                            for k in inbox:
                                try:
                                    update_time = k.get_text()
                                    if update_time.find('16') == 0:
                                        page_update_time = update_time
                                        break
                                except Exception, e:
                                    logging.debug('error msg is page_update_time %s' % str(e))
                            if page_update_time == 0:
                                page_update_time == datetime.datetime.now().strftime('%Y-%m-%d').replace('20','')
                            if uplink:
                                for i in uplink:
                                    if switch_num > self.switch_num:
                                        logging.info('{} time to switch cookie'.format(self.module_name))
                                        self.get_cookie()
                                        switch_num = 0
                                    sum_count += 1
                                    urllink = i['href']
                                    x = i['tag'].replace('_1', '')
                                    prefixid = 'z_' + str(x)
                                    addtime = '20' + page_update_time + ' 00:00:00'
                                    r = self.rp
                                    # if self.resume_exist_chk(x):
                                    #     logging.info('resume %s already exist' % str(x))
                                    if r.rcheck(prefixid, addtime, 1):
                                        #         flag = True
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
                                                urlhtml = self.url_get(urllink)
                                                # urlhtml = self.proxy_url_get(urllink, self.address)
                                                # print 'use current proxy ip',self.address
                                                # while not urlhtml:
                                                #     print 'wrong????',urlhtml
                                                #     if self.test_proxy():
                                                #         print 'use another proxy ip',self.address
                                                #         urlhtml = self.proxy_url_get(urllink, self.address)
                                                isResume = self.isResume_chk(urlhtml)
                                                if isResume == -2:
                                                    req_count =0
                                                elif isResume == -1:
                                                    req_count =3
                                                elif isResume == 4:
                                                    txt_title = self.module_name + 'max limit!!'
                                                    txt_msg = self.module_name + '<br>cookie path'+ self.cookie_fpath+ '<br>'+'current:id_number:'+ str(x) + '<br>' + urlhtml
                                                    self.send_mails(txt_title, txt_msg, 0)
                                                    logging.info('waring! More than the largest number at %s ' % str(x))
                                                    time.sleep(6000*2)
                                                elif isResume == 1:
                                                    switch_num += 1
                                                    if self.save_resume(str(x), urlhtml):                # 默认id长度为23
                                                        seg_success_count += 1
                                                        add_total_num(os.path.split(self.taskfpath)[-1])
                                                        r.tranredis('zhilian', 1, ext1=self.username, ext2='ok', ext3='')
                                                        data_total_add(self.module_name)               # 写入记录到数据库
                                                        try:
                                                            es_redis = r.es_check(prefixid)
                                                            if es_redis == 0:
                                                                data_back = ExtractSegInsert.fetch_do123(urlhtml, 'zhilian', 1)
                                                            elif es_redis == 1:
                                                                data_back = ExtractSegInsert.fetch_do123(urlhtml,'zhilian', -1)
                                                            resume = data_back[0]
                                                            ex_result = data_back[1]
                                                            print ex_result,resume
                                                            if ex_result == 1:
                                                                r.tranredis('zhilian_seg', 1, ext1='insert', ext2='ok')
                                                                r.es_add(prefixid, addtime, 1)
                                                                seg_success_ex += 1
                                                            elif ex_result == -1:
                                                                r.tranredis('zhilian_seg', 1, ext1='update', ext2='ok')
                                                                r.es_add(prefixid, addtime, 1)
                                                                seg_cover_ex += 1
                                                            elif ex_result == -4:
                                                                r.tranredis('zhilian_seg', 1, ext1='update', ext2='search_err')
                                                                r.es_add(prefixid, addtime, 1)
                                                            elif ex_result == 0:
                                                                r.tranredis('zhilian_seg', 1, ext1='insert', ext2='not_insert')
                                                                r.es_add(prefixid, addtime, 0)
                                                            elif ex_result == -2:
                                                                r.tranredis('zhilian_seg', 1, ext1='', ext2='parse_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                                error_path = os.path.join('error/zhilian', str(x)+'.html')
                                                                with open(error_path, 'w+') as f:
                                                                    f.write(urlhtml)
                                                            elif ex_result == -3:
                                                                r.tranredis('zhilian_seg', 1, ext1='', ext2='source_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                            elif ex_result == -5:
                                                                r.tranredis('zhilian_seg', 1, ext1='', ext2='operate_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                        except Exception, e:
                                                            print traceback.format_exc()
                                                            logging.warning('zhilian resume_id %s extractseginsert fail error msg is %s' %(str(x), e))
                                                    else:
                                                        pass
                                                    break
                                                elif isResume == 2:
                                                    logging.info('resume_id %s is secrect resume.' % str(x))
                                                    r.tranredis('zhilian', 1, ext1=self.username, ext2='secret')
                                                    break
                                                elif isResume == 3:
                                                    logging.info('resume_id %s is removed by system.'% str(x))
                                                    r.tranredis('zhilian', 1, ext1=self.username, ext2='removed')
                                                    break
                                                elif isResume == 5:
                                                    r.tranredis('zhilian', 1, ext1=self.username, ext2='busy')
                                                    logging.info('too more busy action and have a rest')
                                                    time.sleep(20*60)
                                                    break
                                                elif isResume == 6:
                                                    txt_title = self.module_name + '请求量过大导致系统无法处理您的请求，您需要输入验证码才能继续后续的操作'
                                                    txt_msg = self.module_name + '<br>cookie path'+ self.cookie_fpath+ '<br>'+'当前抓取id_number:'+ str(x) + '<br>' + urlhtml
                                                    self.send_mails(txt_title, txt_msg, 0)
                                                    logging.info('waring!requst too much,Please enter the verification code %s ' % str(x))
                                                    req_count = 0
                                                    time.sleep(10*100)
                                            except Exception,e:
                                                logging.debug('get %s resume error and msg is %s' % (str(x),str(e)))
                                        self.rand_sleep()

                                        # if len(self.area_list) == 11:

                                        # if date_list[-1].find('16-') == 0 and self.yester_time > date_list[-1]:             # 判断页面日期大于2天之前退出循环
                                        #     logging.info('break current loop %s' % time.asctime())
                                        #     end = True
                                try:
                                    percent = 0
                                    percent = int((float(seg_success_count)/sum_count)*100)
                                    begin_num, seg_end = 0, 0
                                    data_seg_record(self.module_name,seg_success_count,[begin_num,seg_end,percent])
                                    logging.info('<---++1,%s +++,current_page=%s,swoop success get %d unique resumes and the rate is %d%% ||--->入库新增:%s,入库覆盖:%s  ||--->2,swoop_link=%s *****' % (self.username, str(n), seg_success_count,percent, str(seg_success_ex), str(seg_cover_ex),url))
                                    logging.info('-###3,%s ###- swoop Excatly,page_count=%s,|| latest_id =%s, resume_id=%s,gender=%s,age=%s,work_year=%s, area=%s, degree=%s,resume_update_time=%s ||---> ' % (self.username, total_page, str(x), resume['id'], resume['sex'], resume['age'], resume['work_year'], resume['domicile'], resume['degree'], resume['resume_update_time']) )
                                except Exception, e:
                                    logging.warning('error 4,%s swoop %s' % (self.username,str(e)))

                self.fin_task()
                time.sleep(2000*2)
        except Exception,e:
            print traceback.format_exc()
            logging.debug('error msg is %s' % str(e))
            return False

def add_total_num(fname=''):
    '''功能描述：采用文件方式记录总数'''
    try:
        fpath='zhilian_success'+fname
        org_num = 0
        if os.path.exists(fpath):
            f=open(fpath,'rb')
            org_num=int(f.read())
            f.close()
        f=open(fpath,'wb')
        f.write(str(org_num + 1))
        f.close()
        logging.info('zhilian success get %d resumes now' % (org_num+1))
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False

if __name__ == '__main__':
    print 'test...'
    ck_path=r'C:\python space\fetch\cookie\zhilian.txt'
    tk_path=r'C:\python space\fetch\task\task_0001.txt'
    a=zhilianfetch(ck_path,tk_path)
    a.run_work



