# encoding: utf-8
##Todo clean messy previsous codes(useless) cuz dont need task files anymore 

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
# from dbctrl import *
from bs4 import BeautifulSoup
import re
from time import gmtime, strftime
import json, random
from redispipe import *
from extract_seg_insert import ExtractSegInsert
# import extract_seg_insert.cjolextract_new
import sys, os,logging,time,datetime,urllib,urllib2,urlparse
import selectuser
import libaccount
from logging import debug
#reload(sys)
#sys.setdefaultencoding('utf-8')
import logging.config
import requests
import buy2talent


class mainfetch(BaseFetch):
    def __init__(self, position = '', id_number='', adviser_user=''):
        BaseFetch.__init__(self)

        # 确定是否是调试模式
        ### DEBUG 最后一个参数标示 debug
        if len(sys.argv) >= 5:
            if sys.argv[4] == "debug":
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False
        # if dbug ==1:
        #     self.debug = True
        # else:
        #     self.debug = False
        # 选取合适的 cookie 文件
        self.ctmname=''
        self.username=''
        self.password=''
        self.headers={
            'Host':self.host,
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        self.rp = Rdsreport()
        acc = libaccount.Manage(source='cjol', option='buy')
        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['loggers'][""]['handlers'] = ["file", "stream", "buy", "error"]
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')
        self.logger = common.log_init(__name__, 'cjolbuy2.log')


        username1 = acc.uni_user()
        # username1 = 'qimingguanggao'
        self.has_cookie = True
        if username1:
            self.username = username1
            logging.info('cjol buy select username is {}'.format(self.username))
            self.logger.info('cjol buy select username is {}'.format(self.username))
            self.headers['Cookie'] = acc.redis_ck_get(self.username)
        else:
            logging.error('no avail login cookie for cjol')
            self.logger.error('no avail login cookie for cjol')
            self.send_mails('Warining, no account for cjoldown', 'no avail login cookie for cjoldown')
            print '没有已经登陆的 cjol cookie文件'
            self.has_cookie = False
            # quit()  # 这里不退出，在runwork那里才 return something
        print 'id num is {}'.format(id_number)
        print 'position is {}'.format(position)
        logging.info('trying to buy id {}'.format(self.id_number))
        self.logger.info('trying to buy id {}'.format(self.id_number))
        self.adviser_user = adviser_user
        self.id_number=id_number
        self.position = position
        self.host=r'rms.cjol.com'        
        self.domain='cjol.com'
        self.module_name='cjoldown'
        self.init_path()
        self .login_wait=300
        self.refer=''

        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags=['<span id="valUserName" style="color:Red;visibility:hidden;">请输入用户名</span>',
                              '<input id="LoginName" name="UserID" type="text" value="" placeholder="请输入用户名" />']
        self.resume_tags=['基本信息','简历编号']
        self.login_success_tag=[]
        
        # self.cookie_fpath=cookie_fpath

        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
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
            self.logger.debug('error msg is %s'% str(e))
            return -1


        
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
        '''功能描述,执行简历下载'''
        # 选取合适的 cookie 文件
        try:
            if not self.has_cookie:
                # 没有可用  cookie  在这里直接退出
                return json.dumps({'status': 'error', 'msg': 'no avail cookie for cjol',
                                       'time': str(datetime.datetime.now())})
            seged_dict = {}
            self.refer = 'http://newrms.cjol.com/resume/detail-{}'.format(self.id_number)
            self.headers['Referer']=self.refer

            self.headers['Host'] = 'newrms.cjol.com'
            # self.headers['Origin'] = 'http://rms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
            debug = self.debug

            if not self.debug:
                db = sqlite3.connect(buy_database_path)
                cursor = db.cursor()
                sql_cr = ''' create table If not EXISTS cjol
                        (
                        id_num varchar(255) PRIMARY key,
                        nam varchar(255),
                        phone varchar(255),
                        email varchar(255),
                        buy_user varchar(255),
                        add_time timestamp DEFAULT (datetime('now','localtime'))
                        )'''
                cursor.execute(sql_cr)
                db.commit()
                sql_se = """ select id_num,nam,phone,buy_user,email,add_time from cjol WHERE id_num='{}' """.format(self.id_number)
                cursor.execute(sql_se)
                data = cursor.fetchall()
                db.close()
                # 缓存一份在 sqlite 防止重复购买， debug的时候可以去掉，重复购买已购买简历
                if len(data) > 0:
                    idnum, name, phone, buy_user, email, add_time = data[0]
                    logging.info('already down this id {} and {} account is {}, buy_time is {}'.format(self.id_number, self.module_name, buy_user, add_time))
                    self.logger.info('already down this id {} and {} account is {}, buy_time is {}'.format(self.id_number, self.module_name, buy_user, add_time))
                    print 'already down this id {} and {} account is {}, buy_time is {}'.format(self.id_number, self.module_name, buy_user, add_time)
                    print "buy_resume_done,{},{},{}".format(name, phone, email)
                    return json.dumps({'name': name, 'phone': phone, 'email': email, 'id': self.id_number,
                                       'status': 'already', 'time': add_time, 'user': buy_user})

                # 解析 bankid
                bankid = '-1'
                url_0 = 'http://newrms.cjol.com/resume/detail-{}'.format(self.id_number)
                html_0 = self.url_get(url_0)
                soupid = BeautifulSoup(html_0,"html5lib")
                bankid = soupid.find('ul', {'class':"single-ul clearfix"}).get('data-bankid')
                print bankid, 'bankid'
                ###################################
                if int(bankid) == -1:  #todo 改为不等号
                    print 'trying to download this id'
                    logging.info('trying to download this id')
                    self.logger.info('trying to download this id')
                    #quit()
                    ### 购买简历
                    url_buy = r"http://newrms.cjol.com/ResumeBank/CkResumeLink"
                    payload = {
                            'JobSeekerID': str(self.id_number),
                            'Label':'hello_resume',
                              }
                    s = requests.Session()
                    s.headers = self.headers
                    html = s.post(url_buy, payload)
                    res = html.json()  # urllib 返回来的实在搞不清编码。。
                    logging.info('data from cjol is {}'.format(res))
                    self.logger.info('data from cjol is {}'.format(res))
                    # todo 找出购买失败时cjol返回什么
                else:
                    logging.info('already download this id {}, parse form page'.format(self.id_number))
                    self.logger.info('already download this id {}, parse form page'.format(self.id_number))
                    print 'already download this id {}, parse form page'.format(self.id_number)


            else:
                print "----- debug down buy"
                #print html
                ### TODO 检查返回的关键词中如果没有"成功下载"这几个字就标示没有下载成功, 出错了直接打印错误信息

                ### 购买完简历接着下载带联系方式等的简历: TODO 这种方式下载简历存在之前个别账户无法拼 URL 访问的潜在问题
            if not self.debug:
                req_count = 0
                while req_count < 3:
                    req_count+=1
                    try:
                        logging.info('begin to get resume %s from internet' % str(self.id_number))
                        self.logger.info('begin to get resume %s from internet' % str(self.id_number))
                        url = r"http://newrms.cjol.com/ResumeBank/ResumeOperation"
                        payload = {
                                'JobSeekerID': str(self.id_number),
                                'Fn':'resume',
                                'bankid': bankid,
                                'Lang':'CN',
                                  }
                        post_data = urllib.urlencode(payload)
                        html = self.url_post(url, post_data)
                        html = json.loads(html)["OtherData"]
                        isResume = self.isResume_chk(html)
                        # print isResume
                        if isResume == -2:
                            req_count = 0
                        elif isResume == -1:
                            req_count = 3
                        elif isResume == 0:
                            self.login()
                            req_count = 0
                        elif isResume == 1:
                            self.save_resume(str(self.id_number),html)
                            try:
                                prefixid = 'c_' + str(self.id_number)
                                addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                r = self.rp
                                r.rcheck(prefixid, addtime)
                                es_redis = r.es_check(prefixid)
                                if es_redis == 0:  # redis 标记 不在库中
                                    ex_result_1 = ExtractSegInsert.fetch_do123(html, 'cjol', 1)
                                    # ex_result_1 = ExtractSegInsert.fetch_do123(html, 'cjol')
                                elif es_redis == 1:  # redis 标记已经在库中
                                    ex_result_1 = ExtractSegInsert.fetch_do123(html, 'cjol', -1)
                                ex_result = ex_result_1[1]
                                # resume = ex_result_1[0]
                                seged_dict = ex_result_1[2]
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
                                logging.warning(
                                    'cjolbuy resume_id %s extractseginsert fail error msg is %s' % (self.id_number, e), exc_info=True)
                            break
                        elif isResume == 2:
                            logging.info('resume_id %s is secrect resume.' % self.id_number)
                            self.logger.info('resume_id %s is secrect resume.' % self.id_number)
                            break
                        elif isResume == 3:
                            logging.info('resume_id %s is a attachement rusume,need view contact first.'% self.id_number)
                            self.logger.info('resume_id %s is a attachement rusume,need view contact first.'% self.id_number)
                            break
                    except Exception,e:
                        logging.debug('get %s resume error and msg ' %  str(self.id_number))
                        self.logger.debug('get %s resume error and msg ' %  str(self.id_number))

            else:
                print "----- debug down bought resume"

            ### 读取本地文件调试
            if self.debug:
                logging.info('cjol down local debug')
                self.logger.info('cjol down local debug')
                with open("22a.html") as f:
                    html = f.read()
            #print html
            ### TODO 需要检查下文件是否正确
            # x = self.id_number
            # self.save_resume(str(x),html)

            ### 最终操作成功返回解析出来的 姓名,电话,Email

            soup = BeautifulSoup(html,'html.parser')     #解析出尾段对应的hiduserid
            # 姓名
            name = soup.select("title")
            # print name[0].string.encode('utf-8')
            try:
                name = name[0].string.strip()
            except:
                logging.error('parser cjol name error')
                self.logger.error('parser cjol name error')
                name = ''
            try:
                print type(name)
                print name.encode('utf-8')
            except Exception as e:
                logging.error('what encoding is name exactly, {}'.format(e))
                self.logger.error('what encoding is name exactly, {}'.format(e))


            table = soup.find_all('table', {'class':'common_box'})
            # print table
            email = ''
            phone = ''
            try:
                for t in table:
                    # print t.find('td', {'class':'common_tit'})
                    if t.find('td', {'class':'common_tit'}).get_text() == u'联系方式':
                        # print t, 999999999
                        contact = soup.find_all('td', {'class':'common_left'})
                        for c in contact:
                            if c.get_text() == u'手机号码：':
                                phone = c.find_next().get_text()
                            if c.get_text() == u'Email：':
                                email = c.find_next().get_text()
            except Exception, e:
                logging.error('parse phone and email error cjol, and error msg is {}'.format(str(e)))
                self.logger.error('parse phone and email error cjol, and error msg is {}'.format(str(e)), exc_info=True)
                print Exception, str(e)
            name = name.encode('utf-8')
            name = name[:name.find('(')]
            print type(name)

            sql = """insert into cjol (id_num, nam, phone, email, buy_user) VALUES ('{}', '{}', '{}', '{}','{}') """\
                .format(self.id_number, name, phone, email, self.username)
            db = sqlite3.connect(buy_database_path)
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            db.close()
            logging.info("buy_resume_done,{},{},{}".format(name, phone, email))
            self.logger.info("buy_resume_done,{},{},{}".format(name, phone, email))
            print "buy_resume_done,{},{},{}".format(name, phone, email) #% (name, phone, email)
            message = {'name': name, 'phone': phone, 'email': email, 'id': self.id_number,
                               'status': 'ok', 'time': str(datetime.datetime.now()), 'user': self.username}
            b2t = buy2talent.BTalent('cjol', self.id_number, phone, name, email, seged_dict)
            if seged_dict == {}:  # 解析错误，现在也可以 插入到mysql 了
                message['ps'] = 'error cannot down resume or parse resume error, , please complete resume manually'
            try:
                b_res = b2t.main()
                self.logger.info('talent_status is {}'.format(b_res))
                if b_res == -1:
                    message['talent_status'] = 'update phone success'
                elif b_res == -2:
                    message['talent_status'] = 'update phone fail'
                elif b_res == -3:
                    message['talent_status'] = 'this source id already has phone'
                elif b_res == -4:
                    message['talent_status'] = 'phone operate error'
                elif b_res == -5:
                    message['talent_status'] = 'parse resume error'
                elif b_res > 0:
                    message['status'] = 'exist'
                    message['talent_status'] = 'phone number already in talent and id is {}'.format(b_res)
                    message['talent_id'] = b_res
                else:
                    message['talent_status'] = 'error, no correct data'
                b2t.contant_up(message, self.adviser_user)
            except Exception as e:
                message['talent_status'] = 'buy to talent error'
                self.logger.error('buy to talent error', exc_info=True)
            return json.dumps(message)
        except Exception,e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print Exception, str(e)
            logging.critical('error and error msg is {}'.format(str(e)))
            self.logger.critical('error and error msg is {}'.format(str(e)))
            self.send_mails('warnning, cjoldown err', 'cjol down id {} err msg is {}'.format(self.id_number, e))
            print (exc_type, exc_tb.tb_lineno)
            logging.error('error msg is %s' % str(e))
            self.logger.error('error msg is %s' % str(e))
            return json.dumps({'status': 'python error', 'msg': e, 'time': str(datetime.datetime.now()),
                               'user': self.username})


### 调试: python main.py  cjoldown gz 300584521 debug
if __name__ == '__main__':
    print 'test...'
    a=mainfetch('gz',"6823917")
    a.run_work()
