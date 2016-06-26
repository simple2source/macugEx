#-*- coding:UTF-8 -*-

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
from dbctrl import *

class cjolfetch(BaseFetch):
    def __init__(self,cookie_fpath='',task_fpath=''):
        BaseFetch.__init__(self)
        if os.path.exists(cookie_fpath):
            self.load_cookie(cookie_fpath)
        else:
            logging.debug('cookie file %s not exit.' % cookie_fpath)
            exit()
        
        
        self.host=r'rms.cjol.com'        
        self.domain='cjol.com'
        self.module_name='cjol'
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
        self.need_login_tags=['<span id="valUserName" style="color:Red;visibility:hidden;">请输入用户名</span>',
                              '<input id="LoginName" name="UserID" type="text" value="" placeholder="请输入用户名" />']
        self.resume_tags=['基本信息','简历编号']
        self.login_success_tag=[]
        
        self.cookie_fpath=cookie_fpath
        self.taskfpath=task_fpath
        self.inuse_taskfpath=''
        
        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
        self.maxsleeptime=0
    
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
            self.load_task()
            begin_num=self.current_num
            self.refer = 'http://rms.cjol.com/SearchEngine/KeywordSearch.aspx'
            self.headers['Refer']=self.refer 
            self.load_cookie(self.cookie_fpath)
            
            while begin_num < self.end_num:
                if (begin_num+100) > self.end_num:
                    seg_end = self.end_num
                else:
                    seg_end = begin_num+100
                seg_success_count = 0
                for x in range(begin_num,seg_end+1):                    
                    self.current_num = x
                    self.update_task()
                    #self.load_cookie(self.cookie_fpath)
                    if self.resume_exist_chk(str(x)):
                        logging.info('resume %s already exist.' % str(x))
                        seg_success_count += 1
                    else:                        
                        req_count = 0
                        while req_count < 3:
                            req_count += 1
                            try:
                                logging.info('begin to get resume %s from Internet' % str(x))
                                url = r"http://rms.cjol.com/ResumeBank/Resume.aspx?JobSeekerID=%s" % str(x)
                                html = self.url_get(url)                                
                                isResume = self.isResume_chk(html)
                                if isResume == -2:
                                    req_count = 0
                                elif isResume == -1:
                                    req_count = 3
                                elif isResume == 0:
                                    self.login()
                                    req_count = 0
                                elif isResume == 1:
                                    self.save_resume(str(x),html)  
                                    seg_success_count += 1
                                    data_total_add(self.module_name)
                                    add_total_num(os.path.split(self.taskfpath)[-1])
                                    break
                                elif isResume == 2:
                                    logging.info('resume_id %d is secrect resume.' % x)
                                    break
                                elif isResume == 3:
                                    logging.info('resume_id %d is a attachement rusume,need view contact first.'% x)
                                    break                                
                            except Exception,e:
                                logging.debug('get %d resume error and msg is %s' % (x,str(e))) 
                    self.rand_sleep()
                percent = 0
                percent = int((float(seg_success_count)/(seg_end + 1 - begin_num))*100)
                data_seg_record(self.module_name,seg_success_count,[begin_num,seg_end,percent])
                logging.info('success get %d resumes at %d - %d and the rate is %d%%' % (seg_success_count,begin_num,seg_end,percent))
                begin_num = seg_end
            self.fin_task()
            return True
        except Exception,e:
            logging.debug('error msg is %s' % str(e))
            return False

def add_total_num(fname=''):
    '''功能描述：采用文件方式记录总数'''
    try:
        fpath='cjol_success_'+fname
        org_num = 0
        if os.path.exists(fpath):
            f=open(fpath,'rb')
            org_num=int(f.read())
            f.close()
        f=open(fpath,'wb')
        f.write(str(org_num + 1))
        f.close()
        logging.info('cjol success get %d resumes now' % (org_num+1))
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False
        
if __name__ == '__main__':
    print 'test...'
    ck_path=r'C:\python space\fetch\cookie\cjol.txt'
    tk_path=r'C:\python space\fetch\task\task_0001.txt'
    a=cjolfetch(ck_path,tk_path)    
    a.run_work()
