#-*- coding:utf-8 -*-

import os,time,datetime
import urllib,urllib2,urlparse
import random
import ConfigParser
import logging
from common import *
from log import *

class BaseFetch(object):
    
    def __init__(self):
        self.root_path=root_path
        #简历保留根目录
        self.db_root=db_root
        self.db_dir=''
        #cookie目录
        self.cookie_root=cookie_root
        self.cookie_dir=''
        #任务路径，分为原始任务路径、执行任务路径和已完成任务路径
        self.task_root=task_root
        self.task_dir=''
        self.task_inuse_dir=''
        self.task_fin_dir=''
        #出错信息路径
        self.error_root=error_root
        self.error_dir=''
        #是否开启调试模式
        self.debug=False  
        
        #配置服务器host domain 书数据源模块名称等
        self.host=''        
        self.domain=''
        self.module_name=''
        
        #配置企业名、用户名、密码等信息
        self.ctmname=''
        self.username=''
        self.password=''
        
        #配置请求的头部信息
        self.refer=''
        self.headers={}
        
        #cookie字符串、路径、文件修改时间
        self.cookie=''
        self.cookie_fpath=''
        self.cookie_modtime=None
        
        #登录方式、登录状态、登录时间、以及检查登录成功标记等信息
        self.login_type=0#默认：0，user/password:1,cookie:2
        self.islogin=False
        self.login_wait=300
        self.login_at = None
        self.logout_at = None
        self.need_login_tags = ['login']
        self.login_success_tag = []
        self.resume_tags=[]
        
        #单个请求的尝试的最大次数
        self.request_try_times=3
        
        #所执行任务的类型、存放路径等信息
        self.task_type = 0#0:表示默认类型(未知)
        self.taskfpath = ''
        self.id_number = ''
        # 一些ua，用来随机
        self.ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
            'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0',
            'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        ]
        self.ua =  'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
        # 随机ip
        self.proxy_list = ['10.4.16.39:8888', None]  # none 表示为 走本地, 可以加多丶代理地址
        
        #随机休眠的最大秒数
        self.maxsleeptime=10
        
        #记录最近的出错时间以及短时间内的出错次数
        self.last_error_at=None
        self.recent_error_count=0
        
    def init_path(self):
        '''功能描述：必要的路径初始化'''
        try:
            if self.module_name:
                self.db_dir=os.path.join(self.db_root,self.module_name)
                if not os.path.exists(self.db_dir):
                    os.makedirs(self.db_dir)
                self.cookie_dir=os.path.join(self.cookie_root,self.module_name)
                if not os.path.exists(self.cookie_dir):
                    os.makedirs(self.cookie_dir)
                self.error_dir = os.path.join(self.error_root,self.module_name)
                if not os.path.exists(self.error_dir):
                    os.makedirs(self.error_dir)
                self.task_dir=os.path.join(self.task_root,self.module_name)
                if not os.path.exists(self.task_dir):
                    os.makedirs(self.task_dir)
                self.task_inuse_dir=os.path.join(self.task_dir,'inuse')
                if not os.path.exists(self.task_inuse_dir):
                    os.makedirs(self.task_inuse_dir)
                self.task_fin_dir= os.path.join(self.task_dir,'finish')
                if not os.path.exists(self.task_fin_dir):
                    os.makedirs(self.task_fin_dir)
                
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False

    def rand_ua(self):
        try:
            self.ua = random.choice(self.ua_list)
            logging.debug('switch ua to {}'.format(self.ua))
            self.headers['User-Agent'] = self.ua
        except Exception as e:
            logging.error('switch ua err', exc_info=True)
            return False

    def load_cookie(self,fpath):  
        '''功能描述：从文件载入cookie字符串，并添加到header变量'''
        try:
            logging.info('begin to load cookie from %s' % fpath)
            tmpstr=''
            if os.path.exists(fpath):
                f=open(fpath,'rb')
                tmpstr=f.read().strip()
                f.close()                
                self.cookie=tmpstr
                self.cookie_modtime=os.path.getmtime(fpath)
                logging.info('load cookie info success from %s ' % fpath)
                self.headers['Cookie']=tmpstr
            else:
                logging.debug('cookie fpath not exist or cookie file is empty, please check the file.')
            return tmpstr
        except Exception,e:
            logging.debug('load cookie from failed and error is %s ' % str(e))
            return''
    def login(self):
        '''功能描述：用于处理登录过程，cookie失效报警以及自动登陆成功提醒等'''
        pass
    def login_status_chk(self):
        '''功能描述：检查当前登录状态是否有效'''
        pass
    def isResume_chk(self):
        '''功能描述：检查返回内容是否为合格简历'''
        pass
    def run_work(self):
        '''功能描述：执行任务主工作入口函数'''
        pass
    def url_get(self,url,getDict={}):
        '''功能描述：提交GET请求'''
        try:
            count=0
            html = ''
            while count < self.request_try_times:
                html=url_get(url,getDict,self.headers,10) 
                if html:
                    break
                time.sleep(1)
                count += 1
            return html
        except Exception,e:
            logging.debug('error is %s' % str(e))
            return ''

    def proxy_url_get(self,url,ip,getDict={}):
        '''功能描述：提交GET请求'''
        try:
            count=0
            html = ''
            while count < self.request_try_times:
                html = proxy_url_get(url,ip,getDict,self.headers,5)
                if html:
                    break
                time.sleep(1)
                count += 1
            return html
        except Exception,e:
            logging.debug('proxy common error is %s' % str(e))
            return ''

    def proxy_url_post(self,url, ip, postDict={}):
        """通过代理转发post请求"""
        try:
            count = 0
            html = ''
            while count < self.request_try_times:
                html = proxy_url_post(url, ip, postDict, self.headers, 10)
                if html:
                    break
                time.sleep(1)
                count += 1
            return html
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return ''

    def proxy_test_url_get(self,url,ip,getDict={}):
        '''功能描述：提交GET请求'''
        try:
            count=0
            html = ''
            while count < self.request_try_times:
                html = proxy_url_get(url,ip,getDict,self.headers,10)
                if html:
                    break
                time.sleep(1)
                count += 1
            return html
        except Exception,e:
            logging.debug('proxy common error is %s' % str(e))
            return None

    def rand_get(self, url, getDict={}):
        """智联不可以用这个，216的ip被智联封了"""
        try:
            ip = random.choice(self.proxy_list)
            if ip is None:
                html = self.url_get(url, getDict)
            else:
                html = self.proxy_url_get(url, ip, getDict)
            return html
        except Exception, e:
            logging.error('random proxy get error is {}'.format(e), exc_info=True)
            return ''

    def rand_post(self, url, postDict={}):
        """同上，智联别用这个"""
        try:
            ip = random.choice(self.proxy_list)
            if ip is None:
                html = self.url_post(url, postDict)
            else:
                html = self.proxy_url_post(url, ip, postDict)
            return html
        except Exception, e:
            logging.error('random proxy post error is {}'.format(e), exc_info=True)
            return ''

    def url_post(self,url,postDict={}):
        '''功能描述：提交POST请求'''
        try:
            count=0
            html = ''
            while count < self.request_try_times:
                html=url_post(url,postDict,self.headers,10)
                if html:
                    break
                time.sleep(1)
                count += 1
            return html
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return ''
    def resume_exist_chk(self,resume_id=''):
        '''功能描述：根据ID识别对应简历是否已经存在'''
        try:
            flag=False
            resume_id=resume_id.rjust(8,'0')            
            fpath=os.path.join(self.db_dir,resume_id[0:3],resume_id[3:6],resume_id+'.html')
            if os.path.exists(fpath):
                flag=True
            return flag
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False
            
    def save_resume(self,resume_id='',html=''):
        '''功能描述：将简历内容保存至特定文件，拼足8位ID，依次取得0-3 3-6 作为两级目录'''
        try:
            if html and resume_id:
                resume_id=resume_id.rjust(8,'0')            
                fpath=os.path.join(self.db_dir,resume_id[0:3],resume_id[3:6],resume_id+'.html')
                father_dir=os.path.dirname(fpath)
                if not os.path.exists(father_dir):
                    os.makedirs(father_dir)
                if os.path.exists(fpath):
                    os.remove(fpath)
                f=open(fpath+'.tmp','wb')
                f.write(html)
                f.close()
                os.rename(fpath+'.tmp',fpath)
                logging.info('resume %s save success at %s' % (resume_id,fpath))
                return True
            else:
                logging.info('para error and empty parameter found.')
                return False
        except Exception,e:
            logging.debug('error msg is %s' % str(e))    
    def send_mails(self,title='',msg_txt='',msgtype=0):
        '''功能描述：发送email'''
        try:
            if msg_txt:
                sendEmail(self.module_name,title,msg_txt,msgtype)
                logging.info('%s send mail success' % self.module_name)
        except Exception,e:
            logging.debug('error msg is %s' % str(e))

    def save_error_file(self,msg):
        '''功能描述：将错误信息保存这至特定文件'''
        try:
            if msg:
                error_fpath = os.path.join(self.error_dir,'error_'+str(time.time())+'.txt') 
                write_file(error_fpath,msg)
                logging.info('record msg success in file %s' % error_fpath)
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False
            
    def rand_sleep(self):
        '''功能描述：随机休眠，用于模拟手动操作，避免触及抓取限制'''
        try:
            if self.maxsleeptime > 0:
                sleepTime = random.random() * self.maxsleeptime                
                sleepTime = float('%0.2f' % sleepTime)
                logging.info('the spider will sleep %s s' % str(sleepTime))
                time.sleep(sleepTime)
        except Exception,e:            
            logging.debug('error msg is %s ' % str(e))
            time.sleep(random.randint(0,3))
