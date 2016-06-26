#-*- coding:UTF-8 -*-

from BaseFetch import BaseFetch
import os,datetime,time,urlparse,sys
from dbctrl import *
import traceback
import selectuser, liblogin
from redispipe import *
from common import *
from extract_seg_insert import ExtractSegInsert
import libaccount
import selectuser, liblogin
import shutil
import logging.config

class job51fetch(BaseFetch):
    def __init__(self,cookie_fpath='',task_fpath=''):
        BaseFetch.__init__(self)
        if os.path.exists(cookie_fpath):
            self.load_cookie(cookie_fpath)
        else:
            logging.debug('cookie file %s not exit.' % cookie_fpath)
            exit()       

        self.account = libaccount.Manage(source='51job', option='down')
        self.host=r'ehire.51job.com'
        self.domain='51job.com'
        self.module_name='51job'
        self.init_path()
        self .login_wait=300
        
        self.ctmname=''
        self.username=''
        self.password=''
        
        self.refer=''
        self.headers={
            'Host':self.host,                    
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags=['<td colspan="2" class="loginbar">',
                              '<input type="button" onclick="loginSubmit']
        
        self.resume_tags=['<div id="divResume"><style>','简历编号']
        self.login_success_tag=[]
        
        self.cookie_fpath=cookie_fpath
        self.taskfpath=task_fpath
        self.inuse_taskfpath=''
        
        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
        self.maxsleeptime = 11
        self.switch_num = 300
        self.rp = Rdsreport()
        # 下面几个参数是用来选择账号的
        self.time_period = 400
        self.time_num = 150  # 这个跟上面的可以限制选择账号的时候的抓取频率
        self.hour_num = 0
        self.day_num = 0
        self.switch_num = 30
        self.error_username = ['spxx373', 'spxx336', 'huasheng123',
                               u'北京事业部2', u'北京事业部3', u'广州事业部1', u'深圳事业部2']  # 拼接id方式下载失效的帐号
        self.rp = Rdsreport()
        self.task_name = ''
        logger = logging.getLogger(__name__)
        with open(common.json_config_path) as f:
            ff = f.read()
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'job51_id_fetch.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')


    def parse_cookie(self,fpath):
        '''功能描述：从cookie之中解析出来用户名，进而初始化企业名信息'''
        try:
            if os.path.exists(fpath):
                f=open(fpath)
                tmp_str=f.read()
                f.close()
                ck_dict=urlparse.parse_qs(tmp_str)
                if ck_dict.keys().count('UserName') == 1:
                    self.username=ck_dict['UserName'][0]
                    if job51_account_info.has_key(self.username):
                        self.ctmname=job51_account_info[self.username]
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False
    
    def load_task(self):
        '''功能描述：载入任务初始化相关参数'''
        try:
            logging.info('begin to load task from %s' % self.taskfpath)
            task_fname= os.path.split(self.taskfpath)[-1]
            self.task_name = task_fname.split('.')[0]
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
                if html.find('账号异常') > 0:
                    txt_title = self.username + ' 账号异常' + ' ' + self.task_name
                    txt_msg = self.username + '</br>' + html
                    self.send_mails(txt_title, txt_msg, 0)
                    time.sleep(4*5000)
                for item in self.need_login_tags:
                    if item and html.find(item) > -1:
                        flag = 0
                        break
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
            fin_fpath=os.path.join(self.task_fin_dir,task_fname)
            move_file(self.inuse_taskfpath,fin_fpath)
            logging.info('success finish the task %s' % self.taskfpath)
            return True
        except Exception,e:
            logging.debug('error msg is %s ' % str(e))
            return False
        
    def cookie_notice(self,notify_type=0):
        '''功能描述：cookie信息提醒，失效/生效'''
        try:
            if notify_type == 0:
                txt_title = self.module_name+' cookie power off'
                txt_msg=self.module_name
                if self.ctmname:
                    txt_msg += ' 企业名称:'+self.ctmname
                if self.username:
                    txt_msg +=' 用户名:'+self.username
                txt_msg += ' cookie 已经失效，最近一次修改时间:'+ time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.cookie_modtime))
                txt_msg += '<br> cookie path '+self.cookie_fpath
                self.send_mails(txt_title,txt_msg,0)
                cookie_old = self.cookie_fpath
                shutil.copyfile(cookie_old, cookie_old+'_old')
                logging.info('cookie power off and %s send notice_mail success' % self.module_name)
            elif notify_type == 1:
                txt_title = self.module_name+' cookie login success'
                txt_msg=self.module_name
                if self.ctmname:
                    txt_msg += ' 企业名称:'+self.ctmname
                if self.username:
                    txt_msg += ' 用户名:'+self.username
                txt_msg +=  ' cookie 登录成功，cookie最新修改时间:'+ time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.cookie_modtime))
                txt_msg += '<br> cookie path '+self.cookie_fpath
                # self.send_mails(txt_title,txt_msg,0)
                logging.info('cookie login success and %s send notice_mail success' % self.module_name)
            return True
        except Exception,e:
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
                    #exit(0)
                    self.logout_at = datetime.datetime.now()
                    # flag = False
                    self.cookie_notice(0)
                    count = 0
                    while not flag:
                        try:
                            count += 1
                            logging.info('the login action will be executed after %ds ...' % self.login_wait)
                            time.sleep(self.login_wait)
                            if os.path.exists(self.cookie_fpath):           # 判断cookie文件是否存在
                                if os.path.getmtime(self.cookie_fpath) > self.cookie_modtime:
                                    self.load_cookie(self.cookie_fpath)
                                    self.parse_cookie(self.cookie_fpath)
                                    logging.info('cookie file updated at %s' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
                                    logging.info('try to login at the count %d ' % count)
                                    if self.login_status_chk():
                                        flag =True
                                        self.cookie_notice(1)
                                        logging.info('success login at the count %d ' % count)
                                else:
                                    if count % 240 == 0:
                                        self.cookie_notice(0)
                                    read_modtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(self.cookie_fpath)))
                                    record_modtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.cookie_modtime))
                                    logging.info('waite cookie update and modtime_read at %s ,modtime record at %s' % (read_modtime,record_modtime))
                            else:
                                logging.info('cookie file in %s is not exist... ' % self.cookie_fpath)
                                continue
                        except Exception,e:
                            logging.debug('single login error and msg is %s' % str(e))
                    self.login_at=datetime.datetime.now()
                    self.logout_at=None
            return flag
        except Exception,e:
            logging.debug('error msg is %s ' % str(e))
            return False

    def get_cookie(self):    # 更改这里参数来选择账号
        try:
            flag = False
            # self.account = libaccount.Manage(source='51job', option='down')
            redis_key_list = self.account.uni_user(time_period=self.time_period, num=self.time_num, hour_num=self.hour_num, day_num=self.day_num)
            # print redis_key_list, 8888888888
            if len(redis_key_list) > 0:
                while len(redis_key_list) > 0 and not flag:
                    redis_key = random.choice(redis_key_list)
                    redis_key_list.remove(redis_key)
                    self.username = redis_key.split('_')[1].encode('utf-8')
                    logging.info('get username is {}'.format(self.username))
                    # print(self.username), 99999999999
                    if self.username in self.error_username:   # 去掉拼id会失效的帐号
                        continue
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

    def get_cookie_2(self):
        # 更改这里参数来选择账号,指定4个任务跑对应的帐号
        try:
            if self.task_name == 'task_51_27':
                self.username = 'shengde2'
            elif self.task_name == 'task_51_28':
                self.username = 'shengde6'
            elif self.task_name == 'task_51_29':
                self.username = 'shengde7'
            elif self.task_name == 'task_51_30':
                self.username = 'shengde8'
            self.ck_str = self.account.redis_ck_get(self.username)
            self.headers['Cookie'] = self.ck_str
            return True

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

    def login_status_chk(self):
        '''功能描述：检查当前登录状态是否有效'''
        try:
            flag = False
            count =0
            while count < 3:
                count +=1
                try:
                    chk_url = r'http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=10010'
                    self.rand_ua()
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
        
    def run_work(self):
        ''' 功能描述：执行任务主工作入口函数,login会加载cookie '''
        try:
            switch_num = 0
            # self.get_cookie()  暂时禁用掉，会取到购买帐号的cookies
            self.get_cookie_2()
            # self.login2()
            self.load_task()
            begin_num = self.current_num
            # self.load_cookie(self.cookie_fpath)
            # self.parse_cookie(self.cookie_fpath)
            print self.username
            while begin_num < self.end_num:
                if (begin_num+100) > self.end_num:
                    seg_end = self.end_num
                else:
                    seg_end = begin_num+100
                seg_success_count = 0
                seg_error_count = 0
                for x in range(begin_num, seg_end+1):
                    # if switch_num > self.switch_num:
                    #     logging.info('%s time to switch cookie' % self.username)
                    #     self.get_cookie()
                    #     switch_num = 0
                    self.current_num = x
                    self.update_task()
                    prefixid = 'wu_' + str(x)
                    addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    r = self.rp
                    # if self.resume_exist_chk(str(x)):
                    #     logging.info('resume %s already exist.' % str(x))
                    time_stop()
                    if r.rcheck(prefixid, addtime):
                        req_count = 0
                        while req_count < 3:
                            req_count += 1
                            try:
                                logging.info('begin to get resume %s from Internet' % str(x))
                                url = r"http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=%s" % str(x)
                                print url                                                         #修改的
                                self.rand_ua()
                                html = self.url_get(url)
                                isResume = self.isResume_chk(html)
                                if isResume == -2:
                                    req_count = 0
                                elif isResume == -1:
                                    req_count = 3
                                elif isResume == 0:
                                    # self.login2()
                                    time.sleep(300)
                                    self.get_cookie_2()
                                    req_count = 0
                                elif isResume == 1:
                                    if self.save_resume(str(x), html):
                                        seg_success_count += 1
                                        switch_num += 1
                                        data_total_add(self.module_name)
                                        r.tranredis('51job', 1, ext1=self.username, ext2='ok', ext3='')
                                        add_total_num(os.path.split(self.taskfpath)[-1])
                                        try:
                                            es_redis = r.es_check(prefixid)
                                            if es_redis == 0:
                                                data_back = ExtractSegInsert.fetch_do123(html, '51job', 1)
                                            elif es_redis == 1:
                                                data_back = ExtractSegInsert.fetch_do123(html, '51job', -1)
                                            ex_result = data_back[1]
                                            if ex_result == 1:
                                                r.tranredis('51job_seg', 1, ext1='insert', ext2='ok')
                                                r.es_add(prefixid, addtime, 1)
                                            elif ex_result == -1:
                                                r.tranredis('51job_seg', 1, ext1='update', ext2='ok')
                                                r.es_add(prefixid, addtime, 1)
                                            elif ex_result == -4:
                                                r.tranredis('51job_seg', 1, ext1='update', ext2='search_err')
                                                r.es_add(prefixid, addtime, 1)
                                            elif ex_result == 0:
                                                r.tranredis('51job_seg', 1, ext1='insert', ext2='not_insert')
                                                r.es_add(prefixid, addtime, 0)
                                            elif ex_result == -2:
                                                r.tranredis('51job_seg', 1, ext1='', ext2='parse_err')
                                                r.es_add(prefixid, addtime, 0)
                                                error_path = os.path.join('error/51job', str(x)+'.html')
                                                with open(error_path, 'w+') as f:
                                                    f.write(html)
                                            elif ex_result == -3:
                                                r.tranredis('51job_seg', 1, ext1='', ext2='source_err')
                                                r.es_add(prefixid, addtime, 0)
                                            elif ex_result == -5:
                                                r.tranredis('51job_seg', 1, ext1='', ext2='operate_err')
                                                r.es_add(prefixid, addtime, 0)
                                        except Exception,e:
                                            print traceback.format_exc()
                                            logging.warning('51job resume_id %s extractseginsert_fail error msg is %s' %(str(x), e))
                                    else:
                                        pass
                                    break
                                elif isResume == 2:
                                    logging.info('resume_id %d is secret resume.' % x)
                                    r.tranredis('51job', 1, ext1=self.username, ext2='secret')
                                    seg_error_count += 1
                                    break
                                elif isResume == 3:
                                    logging.info('resume_id %d is removed by system.'% x)
                                    r.tranredis('51job', 1, ext1=self.username, ext2='removed')
                                    seg_error_count += 1
                                    print url
                                    break 
                                elif isResume == 4:
                                    logging.info('too more busy action and have a rest')
                                    r.tranredis('51job', 1, ext1=self.username, ext2='busy')
                                    time.sleep(20*60)
                                    break 
                            except Exception,e:
                                logging.debug('get %d resume error and msg is %s' % (x,str(e))) 
                        self.rand_sleep()
                percent = 0
                percent = int((float(seg_success_count)/(seg_end + 1 - begin_num))*100)
                data_seg_record(self.module_name,seg_success_count,[begin_num,seg_end,percent])
                add_process_fetch_count(self.task_name, seg_success_count, seg_error_count)
                logging.info('success get %d resumes at %d - %d and the rate is %d%%' % (seg_success_count,begin_num,seg_end,percent))
                begin_num = seg_end
            self.fin_task()
            add_total_num(os.path.split(self.taskfpath)[-1], flag=1)
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False


def add_total_num(fname='', flag=0):
    '''功能描述：采用文件方式记录总数'''
    try:
        fpath='51job_success'+fname
        if flag == 1:
            # 当任务完成后，重命名成功个数任务记录
            os.rename(fpath, fpath+'.last')
            return True
        org_num = 0
        if os.path.exists(fpath):
            f=open(fpath,'rb')
            org_num=int(f.read())
            f.close()
        f=open(fpath,'wb')
        f.write(str(org_num + 1))
        f.close()
        logging.info('51job success get %d resumes now' % (org_num+1))
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False


def time_stop():
    # 判断当天的时间20:00进行休眠或者早上8：00后启动抓取
    try:
        while True:
            pub_date = datetime.date.today()
            date_now_8 = datetime.datetime.combine(pub_date, datetime.time(8)).strftime('%Y-%m-%d %H:%M:%S')
            date_now_20 = datetime.datetime.combine(pub_date, datetime.time(20)).strftime('%Y-%m-%d %H:%M:%S')
            date_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if date_now_20 > date_now > date_now_8:
                break
            else:
                time.sleep(3000)
                logging.info('spider sleeping %s -----' % date_now)
    except Exception, e:
        logging.debug('error msg is %s' % str(e))

if __name__ == '__main__':
    print 'test...'
    ck_path=r'C:\python space\fetch\cookie\51.txt'
    tk_path=r'C:\python space\fetch\task\task.txt'
    a=job51fetch(ck_path,tk_path)
    a.run_work()
