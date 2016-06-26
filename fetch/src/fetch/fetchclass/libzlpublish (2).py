# encoding:utf8

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
from dbctrl import *
import sys
import json
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')


class zhilianpub(BaseFetch):
    def __init__(self, cookie_fpath, payload):
        BaseFetch.__init__(self)
        if os.path.exists(cookie_fpath):
            self.load_cookie(cookie_fpath)
        else:
            logging.debug('cookie file %s not exit.' % cookie_fpath)
            exit()
        # try:
        #     with open(json_file) as f:
        #         self.json_string = json.load(f)
        # except Exception, e:
        #     print 'load json_file error', Exception, e
        # self.payload = urllib.urlencode(j_payload(self.json_string))
        self.payload = payload
        self.host=r'jobads.zhaopin.com'
        self.domain='zhaopin.com'
        self.module_name='zlpublish'
        self.init_path()
        self .login_wait=300

        self.ctmname=''
        self.username=''
        self.password=''

        self.refer=''
        self.headers={
            'Host':self.host,
            'Origin':'http://jobads.zhaopin.com',
            'Referer':'http://jobads.zhaopin.com/Position/PositionAdd',
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Language':'zh-CN,zh;q=0.8',
        }

        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags=['<td colspan="2" class="loginbar">',
                              '<input type="button" onclick="loginSubmit']

        self.resume_tags=['<div id="divResume"><style>','简历编号']
        self.login_success_tag=[]

        self.cookie_fpath=cookie_fpath
        # self.taskfpath=task_fpath
        self.inuse_taskfpath=''
        # self.years=['7C1', '7C2', '7C3', '7C4', '7C5', '7C6', '7C7', '7C8']
        self.gender = ['7C0', '7C1']
        self.degree = ['7C5', '7C6', '7C7', '7C8']
        # self.degree = ['7C5', '7C6']
        self.area = ['7C040000', '7C030200', '7C010000', '7C020000']
        # self.area = ['7C040000', '7C030200']
        self.now_time = datetime.datetime.now()
        self.yes_time = self.now_time + datetime.timedelta(days=-2)
        self.yester_time = self.yes_time.strftime('%Y-%m-%d')
        self.years_age_gender = []
        self.area_degree = []

        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
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


    def run_work(self):
        '''功能描述：执行任务主工作入口函数'''
        try:
            # self.load_task()
            # 不需要检查登陆态
            #begin_num=self.current_num
            self.load_cookie(self.cookie_fpath)
            print 11111111111111

            self.refer = 'http://jobads.zhaopin.com/Position/PositionManage'
            self.headers['Referer']=self.refer

            self.headers['Host'] = 'jobads.zhaopin.com'
            # self.headers['Origin'] = 'http://rms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/43.0'

            url = 'http://jobads.zhaopin.com/Position/PositionAdd'

            try:
                html = self.url_get(url)
                soup = BeautifulSoup(html, 'html.parser')
                permission = soup.find('input', {'name': 'HavePermissionToPubPosition'}).get('value')
                self.payload['HavePermissionToPubPosition'] = permission
                self.payload['DateEnd'] = soup.find('input', {'id': 'DateEnd', 'name': 'DateEnd'}).get('value')
                self.payload['PriorityRule'] = soup.find('input', {'id': 'PriorityRule', 'name': 'PriorityRule'}).get('value') # 扣除点数，应该要多个账号看一下
                self.payload['DepartmentId'] = soup.find('input', {'id': 'DepartmentId', 'name': 'DepartmentId'}).get('value')
                self.payload['CanPubPositionQty'] = soup.find('input', {'id': 'CanPubPositionQty', 'name': 'CanPubPositionQty'}).get('value')
                self.payload['IsCorpUser'] = soup.find('input', {'id': 'IsCorpUser', 'name': 'IsCorpUser'}).get('value')
                self.payload['LoginPointId'] = soup.find('input', {'id': 'LoginPointId', 'name': 'LoginPointId'}).get('value')
                self.payload['CompanyAddress'] = soup.find('input', {'id': 'CompanyAddress', 'name': 'CompanyAddress'}).get('value')
                self.payload['btnAddClick'] = 'saveasnotpub'   #todo 保存不发布，改成 'saveandpub'  是发布
                # self.payload['PositionApplyReply'] = '-1'
            except Exception, e:
                print Exception, str(e), 1111111111111112222222222222


            #get stateid form page

            # try to prase the html
            try:
                #login check and send cookie off email
                url_post = 'http://jobads.zhaopin.com/Position/PositionAdd'
                self.headers['Referer'] = 'http://jobads.zhaopin.com/Position/PositionAdd'
                self.headers['Origin'] = 'http://jobads.zhaopin.com'
                self.payload = urllib.urlencode(self.payload)
                html = self.url_post(url_post, self.payload)
                print html
                with open('zlpu.html', 'w+') as f:
                    f.write(html)

            except Exception, e:
                print Exception, str(e), 988888888888888
                pass
        except Exception, e:
            print Exception, str(e), 999999999999999
            pass

if __name__ == '__main__':
    print 'test...'
    # ck_path=r'C:\python space\fetch\cookie\cjol.txt'
    ck_path=r'/home/vagrant/share/fetch/src/fetch/cookie/zl.txt'
    # tk_path=r'C:\python space\fetch\task\task_0001.txt'
    tk_path= json_str
    moudle_name=''#抓取模块名称
    # ck_path=''#cookie路径
    # tk_path=''#task任务路径  json_file
    id_num=''#简历id下载
    # try:
    #     # moudle_name=sys.argv[1]
    #     ck_path=sys.argv[1]
    #     tk_path=sys.argv[2]
    # except:
    #     pass
    # if moudle_name == 'cjol':
    if ck_path and tk_path:
        print 1111111111
        work_line=zhilianpub(ck_path, tk_path)
        work_line.run_work()
    # a=job51pub(ck_path,tk_path)
    # a.maxsleeptime=0
    # a.run_work