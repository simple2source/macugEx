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


class Cjolpub(BaseFetch):
    def __init__(self,cookie_fpath='',payload=''):
        BaseFetch.__init__(self)
        if os.path.exists(cookie_fpath):
            self.load_cookie(cookie_fpath)
        else:
            logging.debug('cookie file %s not exit.' % cookie_fpath)
            exit()
        
        self.payload = payload
        self.host=r'rms.cjol.com'        
        self.domain='cjol.com'
        self.module_name='cjolsearch'
        self.init_path()
        self .login_wait=300
        
        self.ctmname=''
        self.username=''
        self.password=''
        
        self.refer=''
        self.headers={
            'Host':self.host,                    
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags=['<span id="valUserName" style="color:Red;visibility:hidden;">请输入用户名</span>',
                              '<input id="LoginName" name="UserID" type="text" value="" placeholder="请输入用户名" />']
        self.resume_tags=['基本信息','简历编号']
        self.login_success_tag=[]
        
        self.cookie_fpath=cookie_fpath
        self.maxsleeptime=2

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


    def run_work(self):
        '''功能描述：执行任务主工作入口函数'''
        try:
            self.load_cookie(self.cookie_fpath)
            self.refer = 'http://newrms.cjol.com/jobpost/jobpost'
            self.headers['Referer']=self.refer
            self.headers['Host'] = 'newrms.cjol.com'
            self.headers['Origin'] = 'http://newrms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
            url = 'http://newrms.cjol.com/JobPost/SaveJobPostInfo?action=Add&jobpostid=-1'
            try:
                #login check and send cookie off email
                # self.login()
                self.payload = urllib.urlencode(self.payload)
                print self.payload
                html = self.url_post(url, self.payload)
                print html
                with open('cjolp.html', 'w+') as f:
                    f.write(html)
            except Exception,e:
                print 'lalala',Exception,e

        except Exception,e:
            print 'lalala',Exception,e



        
if __name__ == '__main__':
    print 'test...'
    ck_path=r'/vagrant/fetch/src/fetch/cookie/cjolsearch/cjols.txt'
    tk_path=r'/vagrant/fetch/src/fetch/task/cjolsearch/taskzone.txt'
    a=cjolsearchfetch(ck_path,tk_path)    
    a.run_work()
