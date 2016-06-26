# coding: utf-8
'''
按照简历 id 所在地下载(购买)51job

TODO
- 单个账号限制每天只能购买 200 个简历
'''

import sys,os,logging,time,datetime,urllib,urllib2,urlparse

from logging import debug
import selectuser
from BaseFetch import BaseFetch
from common import *
import json, re
from bs4 import BeautifulSoup
from random import choice
import sqlite3
import logging.config
import libaccount


class down51job(BaseFetch):
    def __init__(self,  position = '', id_number=''):
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

        # 选取合适的 cookie 文件
        if position == 'gz':
            ppp = '广州'
        elif position == 'sz':
            ppp = '深圳'
        elif position == 'bj':
            ppp = '北京'
        elif position == 'hz':
            ppp = '杭州'
        elif position == 'sh':
            ppp = '上海'
        else:
            ppp = '%'

        self.ctmname=''
        self.username=''
        self.password=''
        acc = libaccount.Manage(source='51job', option='buy', location=ppp)
        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, '51buy.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')

        self.host=r'ehire.51job.com'
        self.domain='51job.com'
        self.module_name='51jobdown'
        self.init_path()
        self.login_wait=300

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

        self.id_number=id_number
        self.position = position
        self.inuse_taskfpath=''

        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
        self.maxsleeptime = 5

        username1 = acc.uni_user()
        print username1
        print 2222222222
        if username1:
            self.username = username1
            logging.info('cjol buy select username is {}'.format(self.username))
            self.headers['Cookie'] = acc.redis_ck_get(self.username)
        else:
            logging.error('no avail login cookie for cjol')
            print '没有已经登陆的 51job cookie文件'
            quit()
        print 'id num is {}'.format(id_number)
        print 'position is {}'.format(position)
        logging.info('trying to buy id {}, position is {}'.format(self.id_number, self.position))

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

    def cookie_file(self, position):
        '''根据条件加载 cookie, 这里需要包含账号的管理逻辑: 根据地区使用账号, 单账号每日下载不能超过 200'''
        ### TODO 文件名应该采用全句常量/变量配置, 目前不了解暂时不管
        cookie_file_tpl = "/data/spider/cookie/51_{id}.txt"
        user_config = "/data/spider/config/global.json"
        if not os.path.exists(user_config):
            logging.error("there is no config file %s " % user_config)
            exit()
        users = json.loads(open(user_config,'r').read())
        # 选取合适的账户的 cookie
        if not users.has_key('51job'):
            logging.error("no 51job user in config file %s" % user_config)
            exit()

        users_in_rule = {}
        for username in users['51job']:
            userinfo = users['51job'][username]
            # 如果对应的 cookie 文件不存在则表示需要重新登录了, 排除掉
            curr_cookie_file = cookie_file_tpl.replace("{id}", str(userinfo['task']))
            if not os.path.exists(curr_cookie_file):
                continue

            # 如果有下载标识并且为当前 position 则加入到候选列表
            if userinfo.has_key("down") and userinfo['down'] == position:
                users_in_rule[username] = userinfo

        # 随机取一个满足条件的
        if len(users_in_rule) < 1:
            logging.error("no valid cookie file for %s" % position)
            exit()
        op_username = choice(users_in_rule.keys())
        op_userinfo = users_in_rule[op_username]
        op_cookie_file = cookie_file_tpl.replace("{id}", str(op_userinfo['task']))
        ### TODO 根据前面找到的对应的用户, 取一个下载量不超过 180 的用户的 cookie 进行下载: 数量检查的逻辑可以暂缓

        if self.debug:
            op_cookie_file = "/data/spider/cookie/51_44.txt"

        # 最后一道保险
        if not os.path.exists(op_cookie_file):
            logging.error("exception for cookie file %s" % op_cookie_file)
            exit()

        return op_cookie_file

    ### 调试: python main.py  down51 gz 300584521 debug
    def run_down(self):
        '''功能描述,执行简历下载'''
        ### TODO 原来的程序构造函数和这里分别有载入 cookie , 感觉是重复的? 不加这里好像又有问题
        # 选取合适的 cookie 文件
        try:
            # position = self.position
            # cookie_fpath = self.cookie_fpath
            # # cookie_fpath = self.cookie_file(position)
            # if not cookie_fpath:
            #     logging.debug('load cookie error for position %s' % position)
            #     exit()
            # if os.path.exists(cookie_fpath):
            #     self.load_cookie(cookie_fpath)
            # else:
            #     logging.debug('cookie file %s not exit.' % cookie_fpath)
            #     exit()
            # # self.login_status_chk()
            #
            # debug = self.debug
            # if self.parse_cookie(cookie_fpath):
            #     print self.username

            ### 购买简历 TODO
            if not self.debug:
                db = sqlite3.connect(buy_database_path)
                cursor = db.cursor()
                sql_cr = ''' create table If not EXISTS job51
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
                sql_se = """ select id_num,nam,phone,buy_user,email,add_time from job51 WHERE id_num='{}' """.format(self.id_number)
                cursor.execute(sql_se)
                data = cursor.fetchall()
                db.close()
                # 缓存一份在 sqlite 防止重复购买， debug的时候可以去掉，重复购买已购买简历
                if len(data) > 0:
                    idnum, name, phone, buy_user, email, add_time = data[0]
                    logging.info('already down this id {} and {} account is {},'
                                 ' buy time is {}'.format(self.id_number, self.module_name, buy_user, add_time))
                    print 'already down this id {} and {} account is {}, buy time is {}'.format(self.id_number, self.module_name, buy_user, add_time)
                    print "buy_resume_done,{},{},{}".format(name, phone, email)
                    quit()

                post_data = 'doType=SearchToCompanyHr&userId=%s&strWhere=' % str(self.id_number)
                url = r"http://ehire.51job.com/Ajax/Resume/GlobalDownload.aspx"
                html = self.url_post(url, post_data)
                print self.id_number
                print html
                if html.find(u'成功下载1份') < 0 and html.find(u'简历已在公司人才夹中') < 0:
                    print '购买失败，购买返回信息如上'
                    logging.critical('51 buy fail')
                    quit()
                else:
                    print '51job id {}, 购买成功'.format(self.id_number)
                    logging.info('51 id {} buy success'.format(self.id_number))
                # if html.find('登录已失效') > 0:


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
                        url = r"http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=%s" % str(self.id_number)
                        html = self.url_get(url)
                        isResume = self.isResume_chk(html)
                        print isResume
                        if isResume == -2:
                            logging.info('error page is %s' % str(self.id_number))
                            break
                        elif isResume ==-1:
                            req_count = 3
                        elif isResume == 0:
                            self.login()
                            req_count = 0
                        elif isResume == 1:
                            self.save_resume(str(self.id_number),html)
                            break
                        elif isResume == 2:
                            logging.info('resume_id %s is secrect resume.' % str(self.id_number))
                            break
                        elif isResume == 3:
                            logging.info('resume_id %s is removed by system.'% str(self.id_number))
                            print url
                            break
                        elif isResume == 4:
                            logging.info('too more busy action and have a rest')
                            time.sleep(20*60)
                            break
                    except Exception,e:
                        logging.debug('get %s resume error and msg ' %  str(self.id_number))

                #     logging.info('begin to get resume %s from internet' % str(self.id_number))
                #     url = r"http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=%s" % str(self.id_number)
                #     html = self.url_get(url)
                #     isResume = self.isResume_chk(html)
                #     if isResume == 1:
                #         x = self.id_number
                #         self.save_resume(str(x),html)
                #     else:
                #         logging.info('resume_id %s is bad' % str(self.id_number))
                #         # break
                # except Exception,e:
                #     logging.debug('get %s resume error and msg ' %  str(self.id_number))
            else:
                print "----- debug down bought resume"

            ### 读取本地文件调试
            if self.debug:
                logging.info('51 bug debug')
                html = open("buy.html").read()
            # print html
            ### TODO 需要检查下文件是否正确
            # x = self.id_number
            # self.save_resume(str(x),html)

            ### 最终操作成功返回解析出来的 姓名,电话,Email

            soup = BeautifulSoup(html,'html.parser')     #解析出尾段对应的hiduserid
            # 姓名
            try:
                name = soup.select("title")
                name = name[0].string.encode('utf-8').strip()
            except:
                name = ''
                logging.error('parser 51job name error')
                pass

            # tds = soup.select("#divResume table table table tr td")
            # phone = tds[7].string.encode('utf-8').strip()
            # email = tds[9].string.encode('utf-8').strip()
            try:
                phone = re.search('1\d{10}', html).group()
            except:
                logging.error('parser 51job phone error')
                phone = ''
            try:
                email = re.search("[\w.]+@[\w.]+", html).group()
            except:
                logging.error('parser 51job email error')
                email = ''
            try:
                sql = """insert into job51 (id_num, nam, phone, email, buy_user) VALUES ('{}', '{}', '{}', '{}','{}') """\
                    .format(self.id_number, name, phone, email, self.username)
                db = sqlite3.connect(buy_database_path)
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
                db.close()
            except:
                logging.error('insert sqlite3 error')
            logging.info("buy_resume_done,%s,%s,%s" % (name, phone, email))
            print "buy_resume_done,%s,%s,%s" % (name, phone, email)
        except Exception,e:
            logging.debug('error msg is %s' % str(e))


