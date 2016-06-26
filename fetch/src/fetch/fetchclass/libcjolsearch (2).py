#-*- coding:UTF-8 -*-
##Todo clean messy previsous codes(useless) cuz dont need task files anymore 

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
from dbctrl import *
from bs4 import BeautifulSoup
import re
from time import gmtime, strftime
import json, random
from redispipe import *
from extract_seg_insert import ExtractSegInsert
# import extract_seg_insert.cjolextract_new
import libaccount
import logging.config




class mainfetch(BaseFetch):
    def __init__(self, aa='', task_fpath=''):
        BaseFetch.__init__(self)

        self.account = libaccount.Manage(source='cjol', option='down')

        self.host=r'rms.cjol.com'        
        self.domain='cjol.com'
        self.module_name='cjolsearch'
        self.init_path()
        self .login_wait=300
        
        self.ctmname=''
        self.username = ''
        self.ck_str = ''
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
        self.need_login_tags=['<span id="valUserName" style="color:Red;visibility:hidden;">请输入用户名</span>',
                              '<input id="LoginName" name="UserID" type="text" value="" placeholder="请输入用户名" />']
        self.resume_tags=['基本信息','简历编号']
        self.login_success_tag=[]
        

        self.taskfpath=task_fpath
        self.inuse_taskfpath=''
        
        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
        self.maxsleeptime=2
        self.rp = Rdsreport()
        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'cjolsearch.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')
        self.time_period = 400
        self.time_num = 150  # 这个跟上面的可以限制选择账号的时候的抓取频率
        self.hour_num = 0
        self.day_num = 0
        self.switch_num = 30

    
    def isResume_chk(self,html):
        '''功能描述：检查返回内容是否为合格简历'''
        try:
            flag = -1
            if html:
                if html.find('该简历已设置为不可查看') > -1:
                    flag = 2
                if html.find('该求职上传了附件简历,查看联系方式后可下载') > -1:
                    flag = 3
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
            # self.load_cookie(self.cookie_fpath)
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
                            if count % 48 == 0:
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
                    chk_url = r'http://rms.cjol.com/ResumeBank/Resume.aspx?JobSeekerID=1'
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
                    if self.login_status_chk():
                        flag = True
                        print self.username * 100
                        logging.info('switching {} username {} success. '.format(self.module_name, self.username))
                    # else:
                    #     sql_res = self.account.sql_password(self.username)
                    #     print sql_res
                    #     self.account.redis_ck_ex(self.username)  # 更新该用户名的cookie失效时间
                    #     self.password = sql_res[1]
                    #     self.ctmname = sql_res[0]
                    #     l_login = liblogin.Login51(cn=self.ctmname.encode('utf-8'), un=self.username, pw=self.password)
                    #     self.ck_str = l_login.main()
                    #     self.headers['Cookie'] = self.ck_str
                    #     if self.login_status_chk():
                    #         self.account.redis_ck_set(self.username, self.ck_str)
                    #         logging.info('51job user {} auto login success'.format(self.username))
                    #         flag = True
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
                                self.send_mails('Warning, No account left for {}'.format(self.module_name), 'time is {}, count is {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), count)
                                logging.critical('no account left for {}'.format(self.module_name))
                        except Exception,e:
                            print Exception, e
                            logging.debug('single login error and msg is %s' % str(e))
            return flag
        except Exception, e:
            logging.error('login process error and error msg is {}'.format(str(e)), exc_info=True)
            return False

    def run_work(self):
        '''功能描述：执行任务主工作入口函数'''
        try:
            #begin_num=self.current_num
            # self.load_cookie(self.cookie_fpath)
            self.get_cookie()
            self.login2()
            self.headers['Cookie'] = self.ck_str
            print self.ck_str
            switch_num = 0
            while True:
                print 22222222222222
                self.refer = 'http://rms.cjol.com/SearchEngine/SearchResumeInCJOL.aspx'
                self.headers['Referer']=self.refer

                self.headers['Host'] = 'rms.cjol.com'
                self.headers['Origin'] = 'http://rms.cjol.com'
                self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'

                # try:
                #     print 1111111111111111
                #
                if self.login_status_chk():
                    print 'login loginininnnnnnnnnn'
                else:
                    self.send_mails('cjol cookie power off', 'cjolsearch {} cookie power off'.format(self.username))
                    self.login2()
                    print 'nononononononon'
                #     #print payload
                # except Exception,e:
                #     print 'lalala',Exception,e
                #     continue
                #
                # get the first resume page
                resumelist = []

                self.refer = 'http://newrms.cjol.com/SearchEngine/List?fn=d'
                self.headers['Referer']=self.refer
                self.headers['Host'] = 'newrms.cjol.com'
                self.headers['Origin'] = 'http://newrms.cjol.com'
                self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
                url = 'http://newrms.cjol.com/SearchEngine/List?fn=d'
                try:
                    for i in range(1,26):
                        payload = {
                                'GetListResult':'GetListResult',
                                'PageSize':'40',
                                'Sort':'UpdateTime desc',
                                'PageNo':'1',
                                  }
                        payload['PageNo'] = str(i)
                        print payload['PageNo']
                        payload = urllib.urlencode(payload)
                        html = self.url_post(url, payload)
                        print 2222222
                        soup = BeautifulSoup(html, "html.parser")
                        try:
                            resume_l = soup.find_all('a', {'class': 'txt-link link-sumnum', 'target': '_blank'})
                            for l in resume_l:
                                resume_link = l.get('href')
                                resume_ii = resume_link[(resume_link.find('-')+1):]
                                print resume_ii
                                resumelist.append(resume_ii)
                        except Exception, e:
                            print Exception, str(e)
                            pass
                except:
                    pass
                logging.info('Got {} resumes total, and {} is unique.'.format(len(resumelist), len(set(resumelist))))
                seg_success_count = 0
                for resumeid in resumelist: #[0:5]:
                    if switch_num > self.switch_num:
                        logging.info('{} time to switch cookie'.format(self.module_name))
                        self.get_cookie()
                        switch_num = 0
                    prefixid = 'c_'+ str(resumeid)
                    addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    r = self.rp
                    #r.tranredis('hasfasf', 1)  #todo 待会删
                    if r.rcheck(prefixid,addtime):
                ## 暂时先分两部分，后面redis id 库足量了，就可以把下个else 去掉
                         req_count = 0
                         # 重试次数3次
                         while req_count < 3:
                             req_count += 1
                             try:
                                 logging.info('begin to get resume %s from Internet' % str(resumeid))
                                 self.refer = 'http://rms.cjol.com/SearchEngine/SearchResumeInCJOL.aspx'
                                 self.headers['Referer']=self.refer
                                 self.headers['Host'] = 'rms.cjol.com'
                                 self.headers['Origin'] = 'http://rms.cjol.com'
                                 self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
                                 url = r"http://rms.cjol.com/ResumeBank/Resume.aspx?JobSeekerID=%s" % str(resumeid)
                                 print url
                                 #print url
                                 html = self.url_get(url)
                                 isResume = self.isResume_chk(html)
                                 if isResume == -2:
                                     req_count = 0
                                 elif isResume == -1:
                                     req_count = 3
                                 elif isResume == 0:
                                     self.login2()
                                     req_count = 0
                                 elif isResume == 1:
                                     switch_num += 1
                                     self.rand_sleep()
                                     self.save_resume(str(resumeid),html)
                                     seg_success_count += 1
                                     data_total_add(self.module_name)
                                     r.tranredis('cjol', 1, ext1=self.username,ext2='ok',ext3='')
                                     add_total_num(os.path.split(self.taskfpath)[-1])
                                     try:
                                         es_redis = r.es_check(prefixid)
                                         if es_redis == 0:  # redis 标记 不在库中
                                             ex_result_1 = ExtractSegInsert.fetch_do123(html, 'cjol', 1)
                                                #ex_result_1 = ExtractSegInsert.fetch_do123(html, 'cjol')
                                         elif es_redis == 1:  # redis 标记已经在库中
                                             ex_result_1 = ExtractSegInsert.fetch_do123(html, 'cjol', -1)
                                         ex_result = ex_result_1[1]
                                         resume = ex_result_1[0]
                                         if ex_result == 1:
                                             r.tranredis('cjol_seg', 1, ext1='insert', ext2='ok')
                                             r.es_add(prefixid, addtime, 1)
                                         elif ex_result == -1:
                                             r.tranredis('cjol_seg', 1, ext1='update', ext2='ok')
                                             r.es_add(prefixid, addtime, 1)
                                         elif ex_result == -4:
                                             r.tranredis('cjol_seg', 1, ext1='update', ext2='search_err')
                                             r.es_add(prefixid, addtime, 1)
                                         elif ex_result == -0:
                                             r.tranredis('cjol_seg', 1, ext1='insert', ext2='not_insert')
                                             r.es_add(prefixid, addtime, 0)
                                         elif ex_result == -2:
                                             r.tranredis('cjol_seg', 1, ext1='', ext2='parse_err')
                                             r.es_add(prefixid, addtime, 0)
                                         elif ex_result == -3:
                                             r.tranredis('cjol_seg', 1, ext1='', ext2='source_err')
                                             r.es_add(prefixid, addtime, 0)
                                         elif ex_result == -5:
                                             r.tranredis('cjol_seg', 1, ext1='', ext2='operate_err')
                                             r.es_add(prefixid, addtime, 0)
                                     except Exception, e:
                                         print '----------'
                                         logging.warning('cjol resume_id %s extractseginsert fail error msg is %s' % (resumeid, e))
                                     break
                                 elif isResume == 2:
                                     logging.info('resume_id %s is secrect resume.' % resumeid)
                                     r.tranredis('cjol', 1, ext1=self.username, ext2='secret')
                                     break
                                 elif isResume == 3:
                                     logging.info('resume_id %s is a attachement rusume,need view contact first.'% resumeid)
                                     r.tranredis('cjol', 1, ext1=self.username, ext2='attach')
                                     break
                             except Exception,e:
                                 logging.debug('get %s resume error and msg is %s' % (resumeid,str(e)))
                percent = 0
                percent = int((float(seg_success_count)/1000)*100)
                begin_num, seg_end = 0, 0   #为了跟dbctrl 兼容
                data_seg_record(self.module_name,seg_success_count,[begin_num,seg_end,percent])
                logging.info('success get %d unique resumes and the rate is %d%%' % (seg_success_count,percent))
                print 'sleeping, 120s'
                logging.info('cjolsearch will sleep 120s')
                time.sleep(60)
                self.rand_sleep()
            
            return True
        except Exception,e:
            logging.debug('errorr msg is %s' % str(e))
            return False

def add_total_num(fname=''):
    '''功能描述：采用文件方式记录总数'''
    try:
        fpath='cjolsearch_success'+fname
        org_num = 0
        if os.path.exists(fpath):
            f=open(fpath,'rb')
            org_num=int(f.read())
            f.close()
        f=open(fpath,'wb')
        f.write(str(org_num + 1))
        f.close()
        logging.info('cjolsearch success get %d resumes now' % (org_num+1))
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False
        
if __name__ == '__main__':
    print 'test...'
    ck_path=r'/vagrant/fetch/src/fetch/cookie/cjolsearch/cjols.txt'
    tk_path=r'/vagrant/fetch/src/fetch/task/cjolsearch/taskzone.txt'
    a=mainfetch(ck_path,tk_path)
    a.run_work()
