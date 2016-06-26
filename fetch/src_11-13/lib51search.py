#-*- coding:UTF-8 -*-


from BaseFetch import BaseFetch
import os,datetime,time,logging,urlparse,sys,cookielib
from common import *
from dbctrl import *
#import html5lib
from bs4 import BeautifulSoup
import urllib,urllib2,cookielib


class job51search(BaseFetch):
    def __init__(self,cookie_fpath='',task_fpath=''):
        BaseFetch.__init__(self)
        if os.path.exists(cookie_fpath):
            self.load_cookie(cookie_fpath)
        else:
            logging.debug('cookie file %s not exit.' % cookie_fpath)
            exit()       
        
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
            'Origin':'http://ehire.51job.com',
            'Referer':'http://ehire.51job.com/Candidate/SearchResume.aspx',
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type':'application/x-www-form-urlencoded', 
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
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
        self.area_list=''
        self.skill_list=''
        self.current_num=self.start_num
        self.maxsleeptime = 5
        
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
            self.area_list = file_str.split("\n")[0].split(',')     #读取本地task文件生成列表
            self.skill_list = file_str.split("\n")[1].split(',')
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
            self.parse_cookie(self.cookie_fpath)
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
                    chk_url = r'http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=10010'
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
        
    def run_search(self):
        '''功能描述：执行任务主工作入口函数,login会加载cookie'''
        try:
            self.load_cookie(self.cookie_fpath)
            self.parse_cookie(self.cookie_fpath)
            #self.load_task()
            self.load_search_task()
            #begin_num=self.current_num
            seg_end = self.end_num 
            seg_success_count = 0
            post_data = '__EVENTTARGET=ctrlSerach%24btnConditionQuery&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKMTUzODk3NDA3OA8WGB4IUGFnZVNpemUCMh4ESXNFTmgeEHZzU2VsZWN0ZWRGaWVsZHMFM0FHRSxXT1JLWUVBUixTRVgsQVJFQSxUT1BNQUpPUixUT1BERUdSRUUsTEFTVFVQREFURR4LTG9nRmlsZU5hbWUFEXNlYXJjaHJlc3VtZS5hc3B4HglQYWdlQ291bnQFAzIwMB4IUGFnZURhdGEF7w0zMDUwMjR8NTMxMjkwfDIxOTIwNDF8NDA3MTU4MXw0NTM1NzA5fDQ2MDQ1MDd8NDYxMzE4NXw0ODYyNzg5fDQ5NzkzOTR8NDk4MDA3NXw1Nzk0ODMzfDY2ODMzODJ8NzU2ODc2MHw3NzQ5OTEwfDc5NzM5Nzl8ODUxNTc2M3w4NTMxMjEwfDg2Nzk0Mzh8ODgzODQ5MXw5MjI0NDI2fDkyMzEyNTl8OTgyMjM1OXwxMDM4NDU0OHwxMDM5MDM1M3wxMDU2NjYxNHwxMTQzODU0NXwxMjkzNTI1NXwxNDkwOTgxM3wxNjA5MzA2NHwxNjE4NzEzOHwxNjIyMzQyOHwxNjI1MTE5N3wxNjYyODczOXwxNzM1NDM1M3wxNzY2Nzg3OXwxODk0MjM3NnwxOTAxMDk5NHwxOTA2MzQ1OXwxOTE1ODg3MnwxOTU1ODU1NnwyNDA4OTc3OXwyNDUzODYyMnwyNDU3MDU0MnwyNDkwNTQyMnwyNTA1MjMxM3wyNTYxMDQzNnwyNjUyNDU4NnwyNzA3NzUzOXwyNzY0ODYyNHwyODQ5MTgwMXwyODg2OTU0NHwyOTA2NzA2M3wyOTEyNzk5MXwyOTc2OTkwMHwzMDA2NjEyN3wzMDE0OTk4N3wzMDYxMTM3NHwzMDcwNDQxNnwzMDc0NTIzNHwzMTQ0MDg4NnwzMTYzODA3OXwzMTkzMTc1M3wzMjU1NDEyNXwzMjU2NDE2M3w0OTEyNjI5OXw1MDY0OTQwOHw1MTEyNzYxMnw1MTE3MTI3NXw1MTc4MDEyMHw1MjE1NzI3M3w1MjIyNjY0MHw1MjI1NDQwNXw1MzAwNTU1OHw1MzQyNzY3NHw1MzYwNjIxNXw1MzcxMDkwOXw1NDQ0MTg1M3w1NjExMTg5NXw1NjQ0NjEyN3w1NzExMjEyMXw1NzIzODU5Mnw1Nzc1MzA5MXw1Nzg4ODExOXw1ODE2MjI0NHw1ODkxMjEyMHw1OTE2Njk0OXw1OTI5NzQwM3w1OTQ1MDMwNHw2MTE1MzEyNnw2MTk3Njk3Mnw2MjEzMDQzNXw2MjE3MzU1NXw2MjY4NTM2NHw2MjkyNDUxMnw2MzAyMzgyMHw2NDExMzcwOHw2NDk0NjUxN3w2NTgzMDcyOHw2NTk0MjY3M3w2NjAzMTY0Nnw2NjMzODc0MXw2NzIzODU1OXw2NzYwNTMyN3w2Nzg5NjAyN3w2ODE3NDMxMnw2ODQxNDcxMXw2OTAzNjkzN3w2OTE2ODQ0NXw2OTMyNDYxOHw2OTQ5NTIzM3w2OTg3Mjk3NHw3MDI3MDk0OHw3MTAyODAzNXw3MTE3NjA3NHw3MTI3NDUwN3w3MTI5ODU0NHw3MTMzMDczNHw3MTQzOTI4OHw3MjE5MTI2OXw3MjMzMjcxMHw3MjQ4MDEyOHw3MzAwNDk1MXw3MzIwODUyOXw3MzI2MTExNHw3MzI5NDE4Mnw3MzM0MDY3NXw3MzU2MTE0MHw3MzcxNjkwMnw3Mzc1NzE1NXw3MzgzMzkwNnw3MzgzODU0OXw3MzkwMjQzOXw3MzkyNDQ3NXw3NDAzMjk4MXw3NDM5MjM4OHw3NDkwMDE5MHw3NTE2NjI4N3w3NTY4MDI3OXw3NzIxNDY2MHw3NzIyOTEzNXw3NzQyNjc1N3w3NzQ0ODQ1MHw3NzU5NDE3MHw3ODc3ODQxOHw3OTE1Nzc0MHw3OTQ1NzM2Nnw3OTczMDc2Mnw3OTgxNzI5OHw4MDExMTk0OHw4MDI5OTM2OXw4MTE3NTQzNnw4MTM1NjA5M3w4MjQ0MDA0NHw4MjQ1ODA0N3w4MjcwMjc4OXw4MzA3NTIxOXw4MzE0MjkxNHw4MzE3NTAwMHw4MzMxMzE2MHw4MzMyMDY1MHw4MzM4ODMzMHw4MzM5NzIyNnw4MzY2MjYxN3w4Mzc3MDU2OXw4Mzc4NjAwMXw4MzgzMzQ5Nnw4NDAzNDc1NXw4NDUyMjg0Nnw4NDc4NTc0Nnw4NTE2MTk3MHw4NTM4NDQwMXw4NTQwMzY4OXw4NTUzNTMyOXw4NTYyMzQ1M3w4NTY0NzkxNHw4NTcxNzEzNHw4NjI1OTc0NHw4NjMwOTE3M3w4NjMzODYwM3w4NjQ1OTE4NHw4NzIyODI2MHw4NzQ1NTEyN3w4ODM4NTIzMHw4ODQ3OTYwMHw4ODUxNTI0N3w4ODUyMjkzOXw4ODc1NjYxMXw4OTAyMTM2MXw4OTE3ODgyOXw4OTYxNzQxNXw4OTcyODE0N3w5MDIzMzU4MHw5MDMyNjM4MXw5MDU2NzEzM3w5MDY2NDgyOHw5MDcyOTA0NHw5MDk2MDUwM3w5MTA4Njc3Nnw5MTA5MTczMnw5MTIzNTc3OB4MVG90YWxSZWNvcmRzArgXHghzdHJDb3VudAUDNTAwHglCZWdpblBhZ2UCAR4NU2VhcmNoVGltZU91dAUCOTQeCVBhZ2VJbmRleGYeB0VuZFBhZ2UCyAEWAgIBD2QWFAIDD2QWBmYPDxYCHgRUZXh0ZWRkAgEPDxYCHwxlZGQCAg8WAh4EaHJlZgUBI2QCBA8PFgweCUV2ZW50RmxhZwUBMB4RSXNDb3JyZWxhdGlvblNvcnQFATEeCFNRTFdoZXJlBcABMDAjMCMxIzB8OTl8MjAxNTA1MDl8MjAxNTExMDl8OTl8OTl8NHw5OXw5OXwwMDAwMDB8MDAwMDAwfDk5fDk5fDk5fDAwMDB8OTl8OTl8OTl8MDB8MDEwNjAxMDcwMTQ0fDk5fDk5fDk5fDAwMDB8OTl8OTl8MDB8OTl8OTl8OTl8OTl8OTl8OTl8OTl8OTl8OTl8MDEwMDAwfDB8MHwwMDAwfDk5IyVCZWdpblBhZ2UlIyVFbmRQYWdlJSNqYXZhHghTUUxUYWJsZQUfU19yZXN1bWVzZWFyY2g2IGEgV0lUSCAoTk9MT0NLKR4FVmFsdWUFwgFLRVlXT1JEVFlQRSMwKkxBU1RNT0RJRllTRUwjNSpKT0JTVEFUVVMjOTkqV09SS1lFQVIjNHw5OSpUT1BERUdSRUUjfCpXT1JLRlVOMSMk6auY57qn6L2v5Lu25bel56iL5biIfDAxMDYk6L2v5Lu25bel56iL5biIfDAxMDck6L2v5Lu2VUnorr7orqHluIgv5bel56iL5biIfDAxNDQkKkVYUEVDVEpPQkFSRUEjMDEwMDAwKktFWVdPUkQjamF2YR8MBYYC566A5Y6G5pu05pawIDog5YWt5Liq5pyI5YaFICA75rGC6IGM54q25oCBIDog5LiN6ZmQICA75bel5L2c5bm06ZmQIDogNC05OSAgO%2BWxheS9j%2BWcsCA6IOmAieaLqS%2Fkv67mlLkgIDvlrabljoYgOiAtICA76KGM5LiaIDog6YCJ5oupL%2BS%2FruaUuSAgO%2BiBjOiDvSA6IOmrmOe6p%2Bi9r%2BS7tuW3peeoi%2BW4iCzova%2Fku7blt6XnqIvluIgs6L2v5Lu2VUnorr7orqHluIgv5bel56iL5biIICA75pyf5pyb5bel5L2c5ZywIDog5YyX5LqsICA75YWz6ZSu5a2XIDogamF2YWQWDAICD2QWAmYPZBYEAgEPEGQQFQES6K%2B36YCJ5oup5pCc57Si5ZmoFQEAFCsDAWcWAWZkAgMPDxYCHwwFBuWIoOmZpBYCHgdvbmNsaWNrBRdyZXR1cm4gY29uZmlybURlbENvbmQoKWQCAw8WBB8TBRhpZighY2hlY2tGb3JtKCkpIHJldHVybjseBXZhbHVlBQbmn6Xor6JkAgQPDxYCHwwFGOS%2FruaUueabtOWkmuafpeivouadoeS7tmRkAgUPZBYCZg9kFgICBQ9kFgoCBw9kFgRmDw8WBB8MBQ3pgInmi6kv5L%2Bu5pS5HgdUb29sVGlwBQ3pgInmi6kv5L%2Bu5pS5ZGQCAQ8WAh8SBQ3pgInmi6kv5L%2Bu5pS5ZAIKDxAPZBYCHghvbkNoYW5nZQVBcmV0dXJuIGlzTUJBKCdjdHJsU2VyYWNoX1RvcERlZ3JlZUZyb20nLCdjdHJsU2VyYWNoX1RvcERlZ3JlZVRvJylkZGQCGQ9kFgRmDw8WBB8MBSLpq5jnuqfova%2Fku7blt6XnqIvluIgs6L2v5Lu25belLi4uHxUFQemrmOe6p%2Bi9r%2BS7tuW3peeoi%2BW4iCzova%2Fku7blt6XnqIvluIgs6L2v5Lu2VUnorr7orqHluIgv5bel56iL5biIZGQCAQ8WAh8SBUHpq5jnuqfova%2Fku7blt6XnqIvluIgs6L2v5Lu25bel56iL5biILOi9r%2BS7tlVJ6K6%2B6K6h5biIL%2BW3peeoi%2BW4iGQCHg9kFgRmDw8WBB8MBQ3pgInmi6kv5L%2Bu5pS5HxUFDemAieaLqS%2Fkv67mlLlkZAIBDxYCHxIFDemAieaLqS%2Fkv67mlLlkAiQPZBYEZg8PFgQfDAUG5YyX5LqsHxUFBuWMl%2BS6rGRkAgEPFgIfEgUG5YyX5LqsZAIGDw8WAh8MBQbmn6Xor6JkZAIOD2QWAmYPZBYEAgEPFgIeCWlubmVyaHRtbAXWLTxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8yIiBuYW1lPSJjaGtfcXVlcnlfMiIgdHlwZT0iY2hlY2tib3giIHZhbHVlPScyJyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiIGNoZWNrZWQ9J2NoZWNrZWQnIGRpc2FibGVkLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMiI%2B5YWz6ZSu5a2XPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMyIgbmFtZT0iY2hrX3F1ZXJ5XzMiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nMycgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiBjaGVja2VkPSdjaGVja2VkJyBkaXNhYmxlZC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzMiPuWxheS9j%2BWcsDwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzYiIG5hbWU9ImNoa19xdWVyeV82IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzYnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgY2hlY2tlZD0nY2hlY2tlZCcgZGlzYWJsZWQvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV82Ij7lrabljoY8L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8yMyIgbmFtZT0iY2hrX3F1ZXJ5XzIzIiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzIzJyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiIGNoZWNrZWQ9J2NoZWNrZWQnIGRpc2FibGVkLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMjMiPueugOWOhuabtOaWsDwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfZGl2X2NsZWFyMiI%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzUiIG5hbWU9ImNoa19xdWVyeV81IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzUnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgY2hlY2tlZD0nY2hlY2tlZCcgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfNSI%2B5bel5L2c5bm06ZmQPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMSIgbmFtZT0iY2hrX3F1ZXJ5XzEiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nMScgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiBjaGVja2VkPSdjaGVja2VkJyAvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV8xIj7ogYzog708L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV80IiBuYW1lPSJjaGtfcXVlcnlfNCIgdHlwZT0iY2hlY2tib3giIHZhbHVlPSc0JyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiIGNoZWNrZWQ9J2NoZWNrZWQnIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzQiPuihjOS4mjwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzgiIG5hbWU9ImNoa19xdWVyeV84IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzgnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgY2hlY2tlZD0nY2hlY2tlZCcgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfOCI%2B5oCn5YirPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9kaXZfY2xlYXIyIj48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMjIiIG5hbWU9ImNoa19xdWVyeV8yMiIgdHlwZT0iY2hlY2tib3giIHZhbHVlPScyMicgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiAgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMjIiPuWbvuaghzwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzciIG5hbWU9ImNoa19xdWVyeV83IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzcnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzciPuW5tOm%2BhDwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzExIiBuYW1lPSJjaGtfcXVlcnlfMTEiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nMTEnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzExIj7kuJPkuJo8L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8yNSIgbmFtZT0iY2hrX3F1ZXJ5XzI1IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzI1JyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiIGNoZWNrZWQ9J2NoZWNrZWQnIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzI1Ij7msYLogYznirbmgIE8L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2Rpdl9jbGVhcjIiPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2Rpdl9jbGVhcjEiPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8yNCIgbmFtZT0iY2hrX3F1ZXJ5XzI0IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzI0JyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiICAvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV8yNCI%2B5pyf5pyb5bel5L2c5ZywPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfOSIgbmFtZT0iY2hrX3F1ZXJ5XzkiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nOScgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiAgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfOSI%2B55uu5YmN5pyI6JaqPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMTAiIG5hbWU9ImNoa19xdWVyeV8xMCIgdHlwZT0iY2hlY2tib3giIHZhbHVlPScxMCcgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiAgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMTAiPuacn%2Bacm%2BaciOiWqjwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzE0IiBuYW1lPSJjaGtfcXVlcnlfMTQiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nMTQnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzE0Ij7miLflj6M8L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2Rpdl9jbGVhcjIiPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8xMyIgbmFtZT0iY2hrX3F1ZXJ5XzEzIiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzEzJyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiICAvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV8xMyI%2BSVTmioDog708L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8xOCIgbmFtZT0iY2hrX3F1ZXJ5XzE4IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzE4JyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiICAvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV8xOCI%2B6Iux6K%2Bt562J57qnPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMTkiIG5hbWU9ImNoa19xdWVyeV8xOSIgdHlwZT0iY2hlY2tib3giIHZhbHVlPScxOScgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiAgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMTkiPuaXpeivreetiee6pzwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzEyIiBuYW1lPSJjaGtfcXVlcnlfMTIiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nMTInIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzEyIj7or63oqIA8L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2Rpdl9jbGVhcjIiPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8xNiIgbmFtZT0iY2hrX3F1ZXJ5XzE2IiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzE2JyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiICAvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV8xNiI%2B5a6e5Lmg57uP6aqMPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMTciIG5hbWU9ImNoa19xdWVyeV8xNyIgdHlwZT0iY2hlY2tib3giIHZhbHVlPScxNycgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiAgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMTciPuWlluWtpumHkTwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfY2hlY2tib3ggaW5ib3hfdmVydGljYWwiPjxpbnB1dCBpZD0iY2hrX3F1ZXJ5XzIwIiBuYW1lPSJjaGtfcXVlcnlfMjAiIHR5cGU9ImNoZWNrYm94IiB2YWx1ZT0nMjAnIG9uY2xpY2s9ImN1c3RvbVF1ZXJ5TnVtcy5jb3VudFF1ZXJ5TnVtcyh0aGlzKSIgIC8%2BPGxhYmVsIGZvcj0iY2hrX3F1ZXJ5XzIwIj7mtbflpJblt6XkvZznu4%2FljoY8L2xhYmVsPjwvZGl2PjxkaXYgY2xhc3M9ImluYm94X2NoZWNrYm94IGluYm94X3ZlcnRpY2FsIj48aW5wdXQgaWQ9ImNoa19xdWVyeV8yMSIgbmFtZT0iY2hrX3F1ZXJ5XzIxIiB0eXBlPSJjaGVja2JveCIgdmFsdWU9JzIxJyBvbmNsaWNrPSJjdXN0b21RdWVyeU51bXMuY291bnRRdWVyeU51bXModGhpcykiICAvPjxsYWJlbCBmb3I9ImNoa19xdWVyeV8yMSI%2B5rW35aSW5a2m5Lmg57uP5Y6GPC9sYWJlbD48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9kaXZfY2xlYXIyIj48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9kaXZfY2xlYXIxIj48L2Rpdj48ZGl2IGNsYXNzPSJpbmJveF9jaGVja2JveCBpbmJveF92ZXJ0aWNhbCI%2BPGlucHV0IGlkPSJjaGtfcXVlcnlfMTUiIG5hbWU9ImNoa19xdWVyeV8xNSIgdHlwZT0iY2hlY2tib3giIHZhbHVlPScxNScgb25jbGljaz0iY3VzdG9tUXVlcnlOdW1zLmNvdW50UXVlcnlOdW1zKHRoaXMpIiAgLz48bGFiZWwgZm9yPSJjaGtfcXVlcnlfMTUiPueugOWOhuivreiogDwvbGFiZWw%2BPC9kaXY%2BPGRpdiBjbGFzcz0iaW5ib3hfZGl2X2NsZWFyMiI%2BPC9kaXY%2BZAICDxYEHxQFBuehruWumh8TBTBpZighY3VzdG9tUXVlcnlOdW1zLmlzT3V0TWF4UXVlcnlOdW1zKCkpIHJldHVybjtkAgUPFgIeBXN0eWxlBQ5kaXNwbGF5OmJsb2NrOxYCZg8PFgIfDAWHAuaCqOebruWJjei%2FmOaciSBbIDxhIGhyZWY9ImphdmFzY3JpcHQ6dm9pZCgwKSIgc3R5bGUgPSJjb2xvcjojMjY2RUI5ICIgb25jbGljaz0iamF2YXNjcmlwdDp3aW5kb3cub3BlbignLi4vQ29tbW9uUGFnZS9Kb2JzRG93bk51bWJMaXN0LmFzcHgnLCdfYmxhbmsnLCdzY3JvbGxiYXJzPXllcyxXaWR0aD00MjhweCxIZWlnaHQ9NDUwcHgscmVzaXphYmxlPXllcycpIj48YiBjbGFzcz0iaW5mb19hdHQiPjUwMDwvYj48L2E%2BIF0g5Lu9566A5Y6G5Y%2Bv5Lul5LiL6L29ZGQCBg8WAh8YBQ1kaXNwbGF5Om5vbmU7ZAIHDxYCHgxVc2VyQnRuV2lkdGgbAAAAAABAU0ABAAAAZAIID2QWDmYPZBYCZg8PFgIfDGVkZAIBDw8WCh8BaB4KUFBhZ2VJbmRleGYfAAIyHwYCuBceE0lzUmVzdW1lQmV0YVJlcXVlc3RnZBYGZg8PFgQeCENzc0NsYXNzBRFjdHJsUGFnaW5hdGlvbkJ0MB4EXyFTQgICZGQCAQ8PFgQfHAURY3RybFBhZ2luYXRpb25CdDAfHQICZGQCAg8PFgQfHAURY3RybFBhZ2luYXRpb25CdDEfHQICZGQCAg8PFgIeCEltYWdlVXJsBU1odHRwOi8vaW1nMDEuNTFqb2JjZG4uY29tL2ltZWhpcmUvZWhpcmUyMDA3L2RlZmF1bHQvaW1hZ2UvaW5ib3gvbGlzdF9vdmVyLmdpZmRkAgMPDxYCHx4FTmh0dHA6Ly9pbWcwMS41MWpvYmNkbi5jb20vaW1laGlyZS9laGlyZTIwMDcvZGVmYXVsdC9pbWFnZS9pbmJveC9kZXRhaWxfb3V0LmdpZmRkAgQPZBYEAgEPDxYEHxwFEXJlc3VtZV9idXR0b24xX29uHx0CAmRkAgMPDxYEHxwFEnJlc3VtZV9idXR0b24xX291dB8dAgJkZAIGDxYCHgdWaXNpYmxlaBYCAgEPDxYCHx4FSWh0dHA6Ly9pbWcwMS41MWpvYmNkbi5jb20vaW1laGlyZS9laGlyZTIwMDcvZGVmYXVsdC9pbWFnZS9zZWFyY2hfbW9yZS5naWZkZAIHDw8WCh8BaB8aZh8AAjIfBgK4Fx8bZ2QWDgIBDw8WCh8MBQMgMSAeD0NvbW1hbmRBcmd1bWVudAUBMR8VBQExHxwFEWN0cmxQYWdpbmF0aW9uQnQxHx0CAmRkAgIPDxYKHwwFAyAyIB8gBQEyHxUFATIfHAURY3RybFBhZ2luYXRpb25CdDAfHQICZGQCAw8PFgofDAUDIDMgHyAFATMfFQUBMx8cBRFjdHJsUGFnaW5hdGlvbkJ0MB8dAgJkZAIEDw8WCh8MBQMgNCAfIAUBNB8VBQE0HxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgUPDxYKHwwFAyA1IB8gBQE1HxUFATUfHAURY3RybFBhZ2luYXRpb25CdDAfHQICZGQCBg8PFgIfDGVkZAIHDw8WAh8MBQMuLi5kZAIJDxYCHxkbAAAAAACAYkABAAAAZAIKDxYCHxkbAAAAAACgYEABAAAAZAILDxYCHxkbAAAAAACAT0ABAAAAZAINDxBkEBURBuW5tOm%2BhAzlt6XkvZzlubTpmZAG5oCn5YirBuaIt%2BWPownlsYXkvY%2FlnLAH6K%2Bt6KiAMQznm67liY3mnIjolqoM5pyf5pyb5pyI6JaqBuS4k%2BS4mgblrabljoYJSVTmioDog70xCUlU5oqA6IO9MgbooYzkuJoG6IGM6IO9EueugOWOhuabtOaWsOaXtumXtAnlrabmoKHlkI0M5rGC6IGM54q25oCBFREDQUdFCFdPUktZRUFSA1NFWAVIVUtPVQRBUkVBA0ZMMQ1DVVJSRU5UU0FMQVJZDEVYUEVDVFNBTEFSWQhUT1BNQUpPUglUT1BERUdSRUUHSVRUWVBFMQdJVFRZUEUyDFdPUktJTkRVU1RSWQhXT1JLRlVOQwpMQVNUVVBEQVRFCVRPUFNDSE9PTBBDVVJSRU5UU0lUVUFUSU9OFCsDEWdnZ2dnZ2dnZ2dnZ2dnZ2dnZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFhYFE2N0cmxTZXJhY2gkZGluZ3l1ZTEFFmN0cmxTZXJhY2gkY2hrX2RlZmF1bHQFB2ltZ0RpczEFB2ltZ0RpczIFDGNieENvbHVtbnMkMAUMY2J4Q29sdW1ucyQxBQxjYnhDb2x1bW5zJDIFDGNieENvbHVtbnMkMwUMY2J4Q29sdW1ucyQ0BQxjYnhDb2x1bW5zJDUFDGNieENvbHVtbnMkNgUMY2J4Q29sdW1ucyQ3BQxjYnhDb2x1bW5zJDgFDGNieENvbHVtbnMkOQUNY2J4Q29sdW1ucyQxMAUNY2J4Q29sdW1ucyQxMQUNY2J4Q29sdW1ucyQxMgUNY2J4Q29sdW1ucyQxMwUNY2J4Q29sdW1ucyQxNAUNY2J4Q29sdW1ucyQxNQUNY2J4Q29sdW1ucyQxNgUNY2J4Q29sdW1ucyQxNg%3D%3D&MainMenuNew1%24CurMenuID=MainMenuNew1_imgResume%7Csub4&ctrlSerach%24hidTab=&ctrlSerach%24hidFlag=&ctrlSerach%24ddlSearchName=&ctrlSerach%24hidSearchID=2%2C3%2C6%2C23%2C5%2C1%2C4%2C25%2C24&ctrlSerach%24hidChkedExpectJobArea=0&ctrlSerach%24KEYWORD=java&ctrlSerach%24KEYWORDTYPE=0&ctrlSerach%24AREA%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24AREA%24Value=&ctrlSerach%24TopDegreeFrom=&ctrlSerach%24TopDegreeTo=&ctrlSerach%24LASTMODIFYSEL=5&ctrlSerach%24WorkYearFrom=4&ctrlSerach%24WorkYearTo=99&ctrlSerach%24WORKFUN1%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24WORKFUN1%24Value=&ctrlSerach%24WORKINDUSTRY1%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24WORKINDUSTRY1%24Value=&ctrlSerach%24JOBSTATUS=99&ctrlSerach%24EXPECTJOBAREA%24Text=%E5%8C%97%E4%BA%AC&ctrlSerach%24EXPECTJOBAREA%24Value=010000&ctrlSerach%24txtUserID=-%E5%A4%9A%E4%B8%AA%E7%AE%80%E5%8E%86ID%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80-&ctrlSerach%24txtSearchName=&chk_query_5=5&chk_query_1=1&chk_query_4=4&chk_query_8=8&chk_query_25=25&pagerBottom%24txtGO=1&cbxColumns%240=AGE&cbxColumns%241=WORKYEAR&cbxColumns%242=SEX&cbxColumns%244=AREA&cbxColumns%248=TOPMAJOR&cbxColumns%249=TOPDEGREE&cbxColumns%2414=LASTUPDATE&hidSearchHidden=&hidUserID=&hidCheckUserIds=305024%2C531290%2C2192041%2C4071581%2C4535709%2C4604507%2C4613185%2C4862789%2C4979394%2C4980075%2C5794833%2C6683382%2C7568760%2C7749910%2C7973979%2C8515763%2C8531210%2C8679438%2C8838491%2C9224426%2C9231259%2C9822359%2C10384548%2C10390353%2C10566614%2C11438545%2C12935255%2C14909813%2C16093064%2C16187138%2C16223428%2C16251197%2C16628739%2C17354353%2C17667879%2C18942376%2C19010994%2C19063459%2C19158872%2C19558556%2C24089779%2C24538622%2C24570542%2C24905422%2C25052313%2C25610436%2C26524586%2C27077539%2C27648624%2C28491801&hidCheckKey=b85f08a2d7d24d91a51d40a6079d6f6c&hidEvents=&hidBtnType=&hidDisplayType=0&hidJobID=&hidValue=KEYWORDTYPE%230*LASTMODIFYSEL%235*JOBSTATUS%2399*WORKYEAR%234%7C99*TOPDEGREE%23%7C*WORKFUN1%23%24%E9%AB%98%E7%BA%A7%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B%E5%B8%88%7C0106%24%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B%E5%B8%88%7C0107%24%E8%BD%AF%E4%BB%B6UI%E8%AE%BE%E8%AE%A1%E5%B8%88%2F%E5%B7%A5%E7%A8%8B%E5%B8%88%7C0144%24*EXPECTJOBAREA%23010000*KEYWORD%23java&hidWhere=00%230%231%230%7C99%7C20150509%7C20151109%7C99%7C99%7C4%7C99%7C99%7C000000%7C000000%7C99%7C99%7C99%7C0000%7C99%7C99%7C99%7C00%7C010601070144%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C010000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23java&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=1'
            url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
            for m in self.area_list:
                for n in self.skill_list:
                    post_data1 = post_data.replace('010000',m).replace('java',n)
                    #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                    #response = opener.open(request,timeout=5)
                    #response = urllib2.urlopen(request)
                    #html = response.read()
                    #proxy = urllib2.ProxyHandler({'http':'192.168.1.69:8888'})
                    #cj = cookielib.CookieJar()
                    #cookie_support = urllib2.HTTPCookieProcessor(cj)
                    #opener = urllib2.build_opener(cookie_support,proxy,urllib2.HTTPHandler)
                    #urllib2.install_opener(opener)
                    #reqs = urllib2.Request(url,post_data1)
                    #reqs1 = urllib2.urlopen(reqs)
                    job51html = open('job51.html','a+')
                    html = self.url_post(url,post_data1)           # 获取网页对象
                    job51html.write(html)
                    job51html.close()
                    soup = BeautifulSoup(open('job51.html'),'html.parser')     #解析出尾段对应的hiduserid
                    uplink = soup.select('.SearchR a')                         #解析出html格式
                    for i in uplink:
                        urllink = r'http://ehire.51job.com/'+i['href']
                        x = urlparse.urlparse(urllink)
                        x = urlparse.parse_qs(x.query,True)
                        x = x['hidUserID'][0]
                        seg_success_count = 0
                #x = x['http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID'][0]
                        self.current_num = x
                #self.update_task()
                        if self.resume_exist_chk(x):
                            logging.info('resume %s already exist.' % str(x))
                            seg_success_count += 1
                        else:
                            req_count = 0
                            while req_count < 3:
                                req_count += 1
                                try:
                                    logging.info('begin to get resume %s from Internet' % str(x))
                                    urlhtml = self.url_get(urllink)
                                    isResume = self.isResume_chk(urlhtml)
                                    if isResume == -2:
                                        req_count = 0
                                    elif isResume == -1:
                                        req_count = 3
                                    elif isResume == 0:
                                        self.login()
                                        req_count = 0
                                    elif isResume == 1:
                                        self.save_resume(str(x),urlhtml)  
                                        seg_success_count += 1
                                        data_total_add(self.module_name)
                                        add_total_num(os.path.split(self.taskfpath)[-1])
                                        break
                                    elif isResume == 2:
                                        logging.info('resume_id %d is secrect resume.' % int(x))
                                        break
                                    elif isResume == 3:
                                        logging.info('resume_id %d is removed by system.'% int(x))
                                        print url
                                        break 
                                    elif isResume == 4:
                                        logging.info('too more busy action and have a rest')
                                        time.sleep(20*60)
                                        break
                                except Exception,e:
                                    logging.debug('get %d resume error and msg is %s' % (x,str(e))) 
                        self.rand_sleep()
                        percent = 0
                        #percent = int((float(seg_success_count)/(seg_end + 1 - begin_num))*100)
                        #data_seg_record(self.module_name,seg_success_count,[begin_num,seg_end,percent])
            #logging.info('success get %d resumes at %d - %d and the rate is %d%%' % (seg_success_count,begin_num,seg_end,percent))
            #begin_num = seg_end
            self.fin_task()
            #return True
                #print urllink
                #print urlnum
            	#urlhtml = self.url_get(urllink)
            	#fpath=os.path.join(self.db_dir+'.html')
                #father_dir=os.path.dirname(fpath)
                #if not os.path.exists(father_dir):
                #    os.makedirs(father_dir)
                #if os.path.exists(fpath):
                #    os.remove(fpath)
                #f=open(fpath+'.tmp','wb')
                #f.write(urlhtml)
                #f.close()
                #os.rename(fpath+'.tmp',fpath)
                #print "done" '''
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False


def add_total_num(fname=''):
    '''功能描述：采用文件方式记录总数'''
    try:
        fpath='51job_success'+fname
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
        
if __name__ == '__main__':
    print 'test...'
    ck_path=r'C:\python space\fetch\cookie\51.txt'
    tk_path=r'C:\python space\fetch\task\task.txt'
    a=job51fetch(ck_path,tk_path)
    a.run_work

