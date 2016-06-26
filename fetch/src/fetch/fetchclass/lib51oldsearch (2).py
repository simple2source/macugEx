#-*- coding:UTF-8 -*-


from BaseFetch import BaseFetch
import os,datetime,time,logging,urlparse,sys,cookielib,datetime
from common import *
from dbctrl import *
#import html5lib
import traceback
from bs4 import BeautifulSoup
import urllib,urllib2,cookielib
from redispipe import *
from extract_seg_insert import ExtractSegInsert


class job51old_search(BaseFetch):
    def __init__(self,cookie_fpath='',task_fpath=''):
        BaseFetch.__init__(self)
        if os.path.exists(cookie_fpath):
            self.load_cookie(cookie_fpath)
        else:
            logging.debug('cookie file %s not exit.' % cookie_fpath)
            exit()

        self.host=r'ehire.51job.com'
        self.domain='51job.com'
        self.module_name='51search'
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
        # self.years=['7C1','7C2','7C3','7C4','7C5','7C6','7C7','7C8']
        # self.years=['7C5', '7C6', '7C7', '7C8', '7C99']
        self.now_time = datetime.datetime.now()
        self.yes_time = self.now_time + datetime.timedelta(days=-2)
        self.seven_ago = (datetime.datetime.now()+datetime.timedelta(days=-7)).strftime('%Y%m%d')
        self.yester_time = self.yes_time.strftime('%Y-%m-%d')
        self.convert_dict = {'7C010000':'北京', '7C020000':'上海', '7C030200':'广州', '7C040000':'深圳', '7C5':'大专', '7C6':'本科', '7C7':'硕士', '7C8':'MBA以上'}

        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.area_list = ['7C040000', '7C020000', '7C030200', '7C010000']
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
            move_file(self.taskfpath, self.inuse_taskfpath)
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
            self.search_list = file_str.split(',')
            # self.area_list = file_str.split("\n")[0].split(',')     #读取本地task文件生成列表,当有多行的时候使用
            # self.skill_list = file_str.split("\n")[1].split(',')
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
            logging.info('%s success crawl finish the task %s' % (self.username, self.taskfpath))
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
                os.rename(cookie_old, cookie_old+'_old')
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
                flag = False
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
            while True:
                self.load_cookie(self.cookie_fpath)
                self.parse_cookie(self.cookie_fpath)
                self.load_search_task()
                print self.yester_time, 'old_search------->>>>>>'
                crawl_count = 0
                url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
                post_data = '__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKMTUzODk3NDA3OA8WGh4Mc3RyU2VsZWN0Q29sBTNBR0UsV09SS1lFQVIsU0VYLEFSRUEsVE9QREVHUkVFLFdPUktGVU5DLExBU1RVUERBVEUeCFBhZ2VTaXplAjIeBElzRU5oHhB2c1NlbGVjdGVkRmllbGRzBTNBR0UsV09SS1lFQVIsU0VYLEFSRUEsVE9QREVHUkVFLFdPUktGVU5DLExBU1RVUERBVEUeC0xvZ0ZpbGVOYW1lBRFzZWFyY2hyZXN1bWUuYXNweB4JUGFnZUNvdW50BQMyMDAeCHN0ckNvdW50BQM1MDAeDVNlYXJjaFRpbWVPdXQFAjE2HgxUb3RhbFJlY29yZHMCuBceCUJlZ2luUGFnZQL5Ch4IUGFnZURhdGEFmg8zMDYxMTQ3Njl8MzIyNDk0NTg3fDMwODI4ODM5MXwzMTc4MDMzMDB8Nzg2NDgyOTZ8OTU4MDk0NTl8OTI1MjkyMDh8OTIxNzM0MTR8ODAzNTExNDd8MzI4NDQzMTI5fDMzNzE3NDQ4OHwzMDQxMDI1MjR8MzM2Nzk1NjAzfDMzNjAzMDkwOHw4OTYzODY3N3w4MDQ3NzcxNXw5MDEzOTI2M3wzMzU2MDgzNTB8ODc0MjgxMDd8MzIwNTA0NjcyfDMzNjg3Nzg2OXwzMTY3OTA5NzZ8MzI1MjU4NTI1fDk2MDY2NjI4fDMyMzc0MjU5MHwzMzQ4Njg0Mzd8MzEyMDA5MDc0fDMyOTczNzUxNHwzMzM5OTgwNDd8MzM2OTcyOTY2fDMwMTc3MzUyNXwzMzYzNDAzNzN8MzM2OTkwMDExfDU2OTIxMjk4fDMwNTY1ODYyMnwzMzU5NjM4MTl8ODA3ODY2ODB8MzAxNDMwMzE5fDMzMjgzNjU4Mnw3OTI0MjE3NXwzMDgyOTIwMTl8MzE2NTc5MzUwfDMxNjA2MzAzNnwzMDA2NDIzNTN8MzM2NTQ0NjI2fDc3NjYzMjEyfDcxMzkyNjA4fDk2ODU1NzI1fDMwNTY1MTQxM3wzMTM5MTc3MzB8OTYwMzY0MzB8OTIyMTAzMTR8MzM0MTU5NzEwfDMxOTA5MjMyOHwzMDQ5MjAyODZ8MzA3NzgxOTc4fDcyNzQ3MDkyfDMzMDA3MTMwNnwzMzU2NDc4MzZ8MzI1MDcyODUzfDMxOTMzNzk1OXwzMzY4NjUzNTd8MzE3ODc4OTQzfDMyNTYzMTI0MnwzMDgzMzQ3MTB8OTYwNDA2NzZ8MzEwNDI2NDg2fDY4MjAzNDU0fDMxODAxMzA0MHwzMzYxOTYxMzB8MzMwMTY0OTQ1fDMzNTIzMjk3N3wzMjI2Mzk4OTl8MzI1NzkyNzI5fDg4OTQxMTQ3fDMyODY2NjQzMnw4Mjc4MDEyMXw3MTMxMzIxNXwzMDc0NzgyMTl8MzM2NTMyMzkxfDk1NDc5NTQ5fDMwNDQ2ODIyNHw3NzUzMjczMnwzMDMwMTU3Njh8MzMzNTc2Nzg4fDk2NjQ4MDIyfDMwODI3MzcyNXw5MzA1ODU3MHw5NTU5MzcxOHwzMzcwODc2Nzl8MzI3ODYyODMyfDgyNzE1NTM2fDMzNjk4NTM3MHw5NjAwODE0OXw5MjY5MDE1OXwzMzAyOTM0NDF8MzI3NDc3NjQ3fDMzNTI2MjM5M3wzMjEzMzQxNjB8MzE4ODkwOTQwfDMyMjQzNDM2N3w4NDE1MTIyNHwzMzY2MzQ4NDZ8OTI5Mjc4MTZ8MzIzMzI4OTExfDMwNTgxODI5NXwzMDI2MjQ5NTZ8MzA1MzY5MDUyfDMzNjMxNTk2MnwzMDc2NDI2MDZ8MzA2NDU0NDk4fDMwNzQzMjAxMHwzMzU3MDU0NzB8MzAwNTIzMzgwfDMzNjU3MzQ2MXw2NjA4MTAzOXwzMzM3NTM1MjV8MzIwNjg0ODg5fDMzNjE0NzMxN3wzMjYyNzQ4MTR8MzM3MTg2OTEyfDMzNzE1MjczMHwzMzQ5MzI4MzB8ODYyMDUxNTB8NzAxODE5MzB8MzE3OTIzNDQxfDMxMTEwOTQwN3wzMzYyNDYyNjV8NjUwOTIzNDR8MzA2NzM2NTQ4fDMyNjAyNjY0MXwzMzcxMDU5MzV8MzE3MzU1MzEwfDkxMzMwMTcwfDMzNjEyMTE5MXwzMDkwNjI3OTZ8MzM2NTgxNTEwfDMyNzI2NDc3M3wzMzQ1MzA3NTR8MzE4OTIwOTAyfDMwNTE1ODM5MXwzMjgwOTM3MjF8MzI3Nzc3MTI4fDgyMDA1MjExfDMyOTk2NDU3MnwzMzUxOTgwNjZ8MzMzMDg3NDEwfDc0MzIxOTAxfDMzNTk3NTExMXwzMjg1MzU0MTF8MzE0NzY4MTE1fDMyNDQ4Njk2NnwzMjIwNDY3OTh8MzAwMTMzMzQyfDMwNzUyNzE2NXw4Mjk3ODAxNHwzMTQ5MDExODV8MzIzOTE4MzM3fDMxMDMwMTA2OXwyNDMxNzE2MnwzMDU5MDQ5NTh8MzE0OTIwNDk0fDMzNzE4NDIzNHwzMzY5NzQ0NDl8OTE1Njg3NTN8MzA1Njc4OTI0fDMwMTA2NjEzNHwzMDQ3ODk3NjJ8MzM2MzQ4NzUxfDMyNTU2MDQwMnwzMjg5NDg1MDV8MzM3MTUwNTM2fDMxNzU3OTE2N3wzMDE5MzYzODB8MzA4MTk3Mjk3fDkzNzE5MDA0fDc4OTU0NDQwfDMzNjQ0MDc2MHwzMjEyNjQ5NzN8MzMzNTQyODc0fDMwNDk1Nzc0NXwzMzcxODU2Nzl8ODY5OTg0NTV8MzM2NDI3OTYxfDMyNjY3MDQ0Nnw5NDA2NjcyM3wzMTY4MzM4MjB8MzM2NzcxMjI2fDMwMTUzNjU3OXw5MDU5NDM4M3w4OTc1MzIwMnwzMTkxMTcyMzB8MzM0ODgwMzUzfDkzMzg2NzkxfDMzNjk5OTEzNnw4NDk3MzQ4NXwzMzQ3NjY1Mjh8ODg5NjI3MjN8MzAzMjM5NzExfDMyMjY0Mjk3OB4JUGFnZUluZGV4Ah8eB0VuZFBhZ2UCwAwWAgIBD2QWFAIDD2QWBmYPDxYCHgRUZXh0ZWRkAgEPDxYCHw1lZGQCAg8WAh4EaHJlZgUBI2QCBA8PFgweCUV2ZW50RmxhZwUBMB4RSXNDb3JyZWxhdGlvblNvcnQFATAeCFNRTFdoZXJlBbMBMDAjMCMwIzB8OTl8MjAxNTA1MjN8MjAxNTExMjN8OTl8OTl8NHw0fDk5fDAwMDAwMHwwMDAwMDB8OTl8OTl8OTl8MDAwMHw5OXw5OXw5OXwwMHwwMDAwfDk5fDk5fDk5fDAwMDB8OTl8OTl8MDB8OTl8OTl8OTl8OTl8OTl8OTl8OTl8OTl8OTl8MDMwMjAwfDB8MHwwMDAwfDk5IyVCZWdpblBhZ2UlIyVFbmRQYWdlJSMeCFNRTFRhYmxlBR9TX3Jlc3VtZXNlYXJjaDYgYSBXSVRIIChOT0xPQ0spHgVWYWx1ZQV8S0VZV09SRFRZUEUjMCpMQVNUTU9ESUZZU0VMIzUqSk9CU1RBVFVTIzk5KldPUktZRUFSIzR8NCpUT1BERUdSRUUjfCpFWFBFQ1RKT0JBUkVBIzAzMDIwMCpLRVlXT1JEI%2BWkmuWFs%2BmUruWtl%2BeUqOepuuagvOmalOW8gB8NBegB566A5Y6G5pu05pawIDog5YWt5Liq5pyI5YaFICA75rGC6IGM54q25oCBIDog5LiN6ZmQICA75bel5L2c5bm06ZmQIDogNC00ICA75bGF5L2P5ZywIDog6YCJ5oupL%2BS%2FruaUuSAgO%2BWtpuWOhiA6IC0gIDvooYzkuJogOiDpgInmi6kv5L%2Bu5pS5ICA76IGM6IO9IDog6YCJ5oupL%2BS%2FruaUuSAgO%2Bacn%2Bacm%2BW3peS9nOWcsCA6IOW5v%2BW3niAgO%2BWFs%2BmUruWtlyA6IOWkmuWFs%2BmUruWtl%2BeUqOepuuagvOmalOW8gGQWDAICD2QWAmYPZBYEAgEPEGQQFQES6K%2B36YCJ5oup5pCc57Si5ZmoFQEAFCsDAWcWAWZkAgMPDxYCHw0FBuWIoOmZpBYCHgdvbmNsaWNrBRdyZXR1cm4gY29uZmlybURlbENvbmQoKWQCAw8WBB8UBRhpZighY2hlY2tGb3JtKCkpIHJldHVybjseBXZhbHVlBQbmn6Xor6JkAgQPDxYCHw0FGOS%2FruaUueabtOWkmuafpeivouadoeS7tmRkAgUPZBYCZg9kFgICBQ9kFgoCBw9kFgRmDw8WBB8NBQ3pgInmi6kv5L%2Bu5pS5HgdUb29sVGlwBQ3pgInmi6kv5L%2Bu5pS5ZGQCAQ8WAh8TBQ3pgInmi6kv5L%2Bu5pS5ZAIKDxAPZBYCHghvbkNoYW5nZQVBcmV0dXJuIGlzTUJBKCdjdHJsU2VyYWNoX1RvcERlZ3JlZUZyb20nLCdjdHJsU2VyYWNoX1RvcERlZ3JlZVRvJylkZGQCGQ9kFgRmDw8WBB8NBQ3pgInmi6kv5L%2Bu5pS5HxYFDemAieaLqS%2Fkv67mlLlkZAIBDxYCHxMFDemAieaLqS%2Fkv67mlLlkAh4PZBYEZg8PFgQfDQUN6YCJ5oupL%2BS%2FruaUuR8WBQ3pgInmi6kv5L%2Bu5pS5ZGQCAQ8WAh8TBQ3pgInmi6kv5L%2Bu5pS5ZAIkD2QWBGYPDxYEHw0FBuW5v%2BW3nh8WBQblub%2Flt55kZAIBDxYCHxMFBuW5v%2BW3nmQCBg8PFgIfDQUG5p%2Bl6K%2BiZGQCDg9kFgJmD2QWAgICDxYEHxUFBuehruWumh8UBTBpZighY3VzdG9tUXVlcnlOdW1zLmlzT3V0TWF4UXVlcnlOdW1zKCkpIHJldHVybjtkAgUPFgIeBXN0eWxlBQ5kaXNwbGF5OmJsb2NrOxYCZg8PFgIfDQWHAuaCqOebruWJjei%2FmOaciSBbIDxhIGhyZWY9ImphdmFzY3JpcHQ6dm9pZCgwKSIgc3R5bGUgPSJjb2xvcjojMjY2RUI5ICIgb25jbGljaz0iamF2YXNjcmlwdDp3aW5kb3cub3BlbignLi4vQ29tbW9uUGFnZS9Kb2JzRG93bk51bWJMaXN0LmFzcHgnLCdfYmxhbmsnLCdzY3JvbGxiYXJzPXllcyxXaWR0aD00MjhweCxIZWlnaHQ9NDUwcHgscmVzaXphYmxlPXllcycpIj48YiBjbGFzcz0iaW5mb19hdHQiPjUwMDwvYj48L2E%2BIF0g5Lu9566A5Y6G5Y%2Bv5Lul5LiL6L29ZGQCBg8WAh8YBQ1kaXNwbGF5Om5vbmU7ZAIHDxYCHgxVc2VyQnRuV2lkdGgbAAAAAABAU0ABAAAAZAIID2QWDmYPZBYCZg8PFgIfDWVkZAIBDw8WCh8CaB4KUFBhZ2VJbmRleAIfHwECMh8IArgXHhNJc1Jlc3VtZUJldGFSZXF1ZXN0Z2QWBmYPDxYEHghDc3NDbGFzcwURY3RybFBhZ2luYXRpb25CdDAeBF8hU0ICAmRkAgEPDxYEHxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgIPDxYEHxwFEWN0cmxQYWdpbmF0aW9uQnQxHx0CAmRkAgIPDxYCHghJbWFnZVVybAVNaHR0cDovL2ltZzAxLjUxam9iY2RuLmNvbS9pbWVoaXJlL2VoaXJlMjAwNy9kZWZhdWx0L2ltYWdlL2luYm94L2xpc3Rfb3Zlci5naWZkZAIDDw8WAh8eBU5odHRwOi8vaW1nMDEuNTFqb2JjZG4uY29tL2ltZWhpcmUvZWhpcmUyMDA3L2RlZmF1bHQvaW1hZ2UvaW5ib3gvZGV0YWlsX291dC5naWZkZAIED2QWBAIBDw8WBB8cBRJyZXN1bWVfYnV0dG9uMV9vdXQfHQICZGQCAw8PFgQfHAURcmVzdW1lX2J1dHRvbjFfb24fHQICZGQCBg8WAh4HVmlzaWJsZWgWAgIBDw8WAh8eBUlodHRwOi8vaW1nMDEuNTFqb2JjZG4uY29tL2ltZWhpcmUvZWhpcmUyMDA3L2RlZmF1bHQvaW1hZ2Uvc2VhcmNoX21vcmUuZ2lmZGQCBw8PFgofAmgfGgIfHwECMh8IArgXHxtnZBYOAgEPDxYKHw0FAjMwHg9Db21tYW5kQXJndW1lbnQFAjMwHxYFAjMwHxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgIPDxYKHw0FAjMxHyAFAjMxHxYFAjMxHxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgMPDxYKHw0FAjMyHyAFAjMyHxYFAjMyHxwFEWN0cmxQYWdpbmF0aW9uQnQxHx0CAmRkAgQPDxYKHw0FAjMzHyAFAjMzHxYFAjMzHxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgUPDxYKHw0FAjM0HyAFAjM0HxYFAjM0HxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgYPDxYCHw0FAy4uLmRkAgcPDxYCHw0FAy4uLmRkAgkPFgIfGRsAAAAAAIBiQAEAAABkAgoPFgIfGRsAAAAAAKBgQAEAAABkAgsPFgIfGRsAAAAAAIBPQAEAAABkAg0PEGQQFREG5bm06b6EDOW3peS9nOW5tOmZkAbmgKfliKsG5oi35Y%2BjCeWxheS9j%2BWcsAfor63oqIAxDOebruWJjeaciOiWqgzmnJ%2FmnJvmnIjolqoG5LiT5LiaBuWtpuWOhglJVOaKgOiDvTEJSVTmioDog70yBuihjOS4mgbogYzog70S566A5Y6G5pu05paw5pe26Ze0CeWtpuagoeWQjQzmsYLogYznirbmgIEVEQNBR0UIV09SS1lFQVIDU0VYBUhVS09VBEFSRUEDRkwxDUNVUlJFTlRTQUxBUlkMRVhQRUNUU0FMQVJZCFRPUE1BSk9SCVRPUERFR1JFRQdJVFRZUEUxB0lUVFlQRTIMV09SS0lORFVTVFJZCFdPUktGVU5DCkxBU1RVUERBVEUJVE9QU0NIT09MEENVUlJFTlRTSVRVQVRJT04UKwMRZ2dnZ2dnZ2dnZ2dnZ2dnZ2dkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WFgUTY3RybFNlcmFjaCRkaW5neXVlMQUWY3RybFNlcmFjaCRjaGtfZGVmYXVsdAUHaW1nRGlzMQUHaW1nRGlzMgUMY2J4Q29sdW1ucyQwBQxjYnhDb2x1bW5zJDEFDGNieENvbHVtbnMkMgUMY2J4Q29sdW1ucyQzBQxjYnhDb2x1bW5zJDQFDGNieENvbHVtbnMkNQUMY2J4Q29sdW1ucyQ2BQxjYnhDb2x1bW5zJDcFDGNieENvbHVtbnMkOAUMY2J4Q29sdW1ucyQ5BQ1jYnhDb2x1bW5zJDEwBQ1jYnhDb2x1bW5zJDExBQ1jYnhDb2x1bW5zJDEyBQ1jYnhDb2x1bW5zJDEzBQ1jYnhDb2x1bW5zJDE0BQ1jYnhDb2x1bW5zJDE1BQ1jYnhDb2x1bW5zJDE2BQ1jYnhDb2x1bW5zJDE2&MainMenuNew1%24CurMenuID=MainMenuNew1_imgResume%7Csub4&ctrlSerach%24hidTab=&ctrlSerach%24hidFlag=&ctrlSerach%24ddlSearchName=&ctrlSerach%24hidSearchID=23%2C25%2C5%2C3%2C6%2C4%2C1%2C24%2C2&ctrlSerach%24hidChkedExpectJobArea=0&ctrlSerach%24KEYWORD=%E5%A4%9A%E5%85%B3%E9%94%AE%E5%AD%97%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80&ctrlSerach%24KEYWORDTYPE=0&ctrlSerach%24AREA%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24AREA%24Value=&ctrlSerach%24TopDegreeFrom=&ctrlSerach%24TopDegreeTo=&ctrlSerach%24LASTMODIFYSEL=5&ctrlSerach%24WorkYearFrom=4&ctrlSerach%24WorkYearTo=4&ctrlSerach%24WORKFUN1%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24WORKFUN1%24Value=&ctrlSerach%24WORKINDUSTRY1%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24WORKINDUSTRY1%24Value=&ctrlSerach%24JOBSTATUS=99&ctrlSerach%24EXPECTJOBAREA%24Text=%E5%B9%BF%E5%B7%9E&ctrlSerach%24EXPECTJOBAREA%24Value=030200&ctrlSerach%24txtUserID=-%E5%A4%9A%E4%B8%AA%E7%AE%80%E5%8E%86ID%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80-&ctrlSerach%24txtSearchName=&pagerBottom%24txtGO=125&pagerBottom%24lbtnGO=+&cbxColumns%240=AGE&cbxColumns%241=WORKYEAR&cbxColumns%242=SEX&cbxColumns%244=AREA&cbxColumns%249=TOPDEGREE&cbxColumns%2413=WORKFUNC&cbxColumns%2414=LASTUPDATE&hidSearchHidden=&hidUserID=&hidCheckUserIds=314768115%2C324486966%2C322046798%2C300133342%2C307527165%2C82978014%2C314901185%2C323918337%2C310301069%2C24317162%2C305904958%2C314920494%2C337184234%2C336974449%2C91568753%2C305678924%2C304789762%2C301066134%2C336348751%2C325560402%2C328948505%2C337150536%2C317579167%2C301936380%2C308197297%2C93719004%2C78954440%2C336440760%2C321264973%2C333542874%2C304957745%2C337185679%2C86998455%2C336427961%2C326670446%2C94066723%2C316833820%2C336771226%2C301536579%2C90594383%2C89753202%2C319117230%2C334880353%2C93386791%2C336999136%2C84973485%2C334766528%2C88962723%2C303239711%2C322642978&hidCheckKey=0674ba4190730c0b29ef13d5436869cc&hidEvents=&hidBtnType=&hidDisplayType=0&hidJobID=&hidValue=KEYWORDTYPE%230*LASTMODIFYSEL%235*JOBSTATUS%2399*WORKYEAR%234%7C4*TOPDEGREE%23%7C*EXPECTJOBAREA%23030200*KEYWORD%23%E5%A4%9A%E5%85%B3%E9%94%AE%E5%AD%97%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80&hidWhere=00%230%230%230%7C99%7C20151231%7C20160107%7C31%7C31%7C7%7C7%7C99%7C000000%7C000000%7C99%7C99%7C99%7C0000%7C99%7C99%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C020000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0'
                for m in self.area_list:
                    for l in self.search_list:
                        #         area_year.append((m,l))
                        # for x in area_year:
                        end = False
                        for n in range(1, 60):
                            seg_success_count = 0
                            sum_count = 0                # 统计循环页面总的简历数
                            seg_success_ex = 0
                            seg_cover_ex = 0
                            if end:
                                break
                            if len(self.search_list) == 8:
                                post_data1 = post_data.replace('7C020000', m).replace('125',str(n)).replace('7C7', l).replace('7C31', '7C99').replace('20151123',time.strftime('%Y%m%d',time.localtime())).replace('20150523', (datetime.datetime.now()+datetime.timedelta(days=-7)).strftime('%Y%m%d'))
                                hidWhere = post_data1[post_data1.find('hidWhere'):]
                            elif len(self.search_list) == 21:
                                post_data1 = post_data.replace('7C020000', m).replace('125', str(n)).replace('7C7', '7C99').replace('7C31', l).replace('20151123',time.strftime('%Y%m%d',time.localtime())).replace('20150523', self.seven_ago)
                                hidWhere = post_data1[post_data1.find('hidWhere'):]
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
                                    html = self.url_post(url, post_data1)
                                    if html.find('id="Login_btnLoginCN"') > 0:
                                        self.login()
                                    if html.find('抱歉，没有搜到您想找的简历') >0:
                                        end = True
                                        time.sleep(20)
                                        break
                                    soup = BeautifulSoup(html, 'html.parser')
                                    uplink = soup.select('.SearchR a')
                                    inbox = soup.select('td.inbox_td4')                       #解析出简历更新时间
                                    total_search_count = soup.select('strong')[0].get_text()
                                    total_page = soup.select('strong')[1].get_text()
                                    total_page_count = int(soup.select('strong')[1].get_text().split('/')[1])
                                    page_update_time = 0
                                    for k in inbox:
                                        try:
                                            update_time = k.get_text()
                                            if update_time.find('2016') == 0:
                                                page_update_time = update_time
                                                break
                                        except Exception, e:
                                            logging.debug('error msg is page_update_time %s' % str(e))
                                    if page_update_time == 0:
                                        page_update_time = datetime.datetime.now().strftime('%Y-%m-%d')
                                    if n == total_page_count:
                                        end = True
                                except Exception,e:
                                    logging.error('51job_latest error work_area %s work_year %s request is %s ...' % (str(m),str(l),str(e)))
                            #解析出html格式
                            if uplink:
                                resume ={'id': '', 'age': '', 'work_year': '', 'degree': '', 'resume_update_time': '', 'domicile': '', 'sex': ''}
                                for i in uplink:
                                    sum_count += 1
                                    urllink = r'http://ehire.51job.com/'+i['href']
                                    x = urlparse.urlparse(urllink)
                                    x = urlparse.parse_qs(x.query,True)
                                    x = x['hidUserID'][0]
                                    #x = x['http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID'][0]
                                    self.current_num = x
                                    print x ,urllink
                                    prefixid = 'wu_' + str(x)
                                    addtime = page_update_time + ' 00:00:00'
                                    r = Rdsreport()
                                    if self.resume_exist_chk(x):
                                        logging.info('resume %s already exist.' % str(x))
                                        if r.rcheck(prefixid, addtime, 1):
                                            flag = True
                                        else:
                                            flag = False
                                    else:
                                        flag = True
                                        r.rcheck(prefixid, addtime, 1)
                                    if flag:
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
                                                    if self.save_resume(str(x),urlhtml):
                                                        seg_success_count += 1
                                                        data_total_add(self.module_name)
                                                        r.tranredis('51search', 1, ext1=self.username, ext2='ok', ext3='')
                                                        add_total_num(os.path.split(self.taskfpath)[-1])
                                                        try:
                                                            es_redis = r.es_check(prefixid)
                                                            if es_redis == 0:
                                                                data_back = ExtractSegInsert.fetch_do123(urlhtml, '51job', 1)
                                                            elif es_redis == 1:
                                                                data_back = ExtractSegInsert.fetch_do123(urlhtml,'51job', -1)
                                                            resume = data_back[0]
                                                            ex_result = data_back[1]
                                                            print ex_result,resume
                                                            if ex_result == 1:
                                                                r.tranredis('51search_seg', 1, ext1='insert', ext2='ok')
                                                                r.es_add(prefixid, addtime, 1)
                                                                seg_success_ex += 1
                                                            elif ex_result == -1:
                                                                r.tranredis('51search_seg', 1, ext1='update', ext2='ok')
                                                                r.es_add(prefixid, addtime, 1)
                                                                seg_cover_ex += 1
                                                            elif ex_result == -4:
                                                                r.tranredis('51search_seg', 1, ext1='update', ext2='search_err')
                                                                r.es_add(prefixid, addtime, 1)
                                                            elif ex_result == 0:
                                                                r.tranredis('51search_seg', 1, ext1='insert', ext2='not_insert')
                                                                r.es_add(prefixid, addtime, 0)
                                                            elif ex_result == -2:
                                                                r.tranredis('51search_seg', 1, ext1='', ext2='parse_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                                error_path = os.path.join('error/51search', str(x)+'.html')
                                                                with open(error_path, 'w+') as f:
                                                                    f.write(urlhtml)
                                                            elif ex_result == -3:
                                                                r.tranredis('51search_seg', 1, ext1='', ext2='source_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                            elif ex_result == -5:
                                                                r.tranredis('51search_seg', 1, ext1='', ext2='operate_err')
                                                                r.es_add(prefixid, addtime, 0)
                                                        except Exception, e:
                                                            print traceback.format_exc()
                                                            logging.warning('51job resume_id %s extractseginsert fail error msg is %s' % (str(x), e))
                                                    else:
                                                        pass
                                                    break
                                                elif isResume == 2:
                                                    logging.info('resume_id %s is secrect resume.' % str(x))
                                                    r.tranredis('51search', 1, ext1=self.username, ext2='secret')
                                                    break
                                                elif isResume == 3:
                                                    logging.info('resume_id %s is removed by system.'% str(x))
                                                    r.tranredis('51search', 1, ext1=self.username, ext2='remove')
                                                    print url
                                                    break
                                                elif isResume == 4:
                                                    logging.info('too more busy action and have a rest')
                                                    r.tranredis('51search', 1, ext1=self.username, ext2='busy')
                                                    time.sleep(20*60)
                                                    break
                                            except Exception,e:
                                                logging.debug('get %s resume error and msg is %s' % (str(x),str(e)))
                                        self.rand_sleep()

                                # if date_list[-7].find('2016') == 0 and self.yester_time > date_list[-7]:             # 判断页面日期大于2天之前退出循环
                                #     end = True
                                #     logging.info('break current loop %s' % time.asctime())

                                percent = 0
                                percent = int((float(seg_success_count)/sum_count)*100)
                                begin_num, seg_end = 0, 0
                                data_seg_record(self.module_name,seg_success_count,[begin_num,seg_end,percent])
                                t1 = time.time() -t0
                                convert_area = self.convert_dict[m]
                                crawl_count += 1
                                logging.info('+++++1,%s ++++ ,已经抓取页面数:%s,take_time=%d s ,current_page = %s , success get %d unique resumes and the rate is %d%% ||--->入库新增:%s,入库覆盖:%s ||--->2,crawl_condition:area=%s,work_year=%s ||--->3,crawl post_data: %s ******' % (self.username, str(crawl_count), t1, str(n), seg_success_count, percent, str(seg_success_ex), str(seg_cover_ex),convert_area, l, hidWhere))
                                try:
                                    logging.info('-####4,%s###-, Excatly 页面简历总数=%s ,page_count=%s,||-->resume_id=%s,age=%s,work_year=%s, area=%s, degree=%s,resume_update_time=%s ####' % (self.username,total_search_count, total_page, resume['id'], resume['age'], resume['work_year'] ,resume['domicile'], resume['degree'], resume['resume_update_time']) )
                                except Exception,e:
                                    logging.debug('error 5,%s crawl transfer is fail %s' % (self.username, str(e)))
                self.fin_task()
                time.sleep(2000*2)
        except Exception,e:
            print traceback.format_exc()
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
    a=job51search(ck_path,tk_path)
    a.run_work

