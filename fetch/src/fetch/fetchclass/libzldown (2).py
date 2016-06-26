#-*- coding:UTF-8 -*-

from BaseFetch import BaseFetch
import os,datetime,time,logging,urlparse,sys,cookielib,traceback
from common import *
from dbctrl import *
from bs4 import BeautifulSoup
import urllib,urllib2
from extract_seg_insert import ExtractSegInsert
import libaccount
from redispipe import *
import selectuser, random
import logging.config
import requests


class mainfetch(BaseFetch):
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

        acc = libaccount.Manage(source='zhilian', option='buy', location=ppp)
        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'zlbuy.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')

        self.id_number=id_number
        self.position = position

        self.host=r'rd.zhaopin.com'
        self.domain='zhaopin.com'
        self.module_name='zhilian'
        self.init_path()
        self .login_wait=300


        self.refer=''
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Origin': 'http://rdsearch.zhaopin.com',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer':'http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_1=java&SF_1_1_4=2%2C99&SF_1_1_18=765&orderBy=DATE_MODIFIED,1&pageSize=60&SF_1_1_27=0&exclude=1',
        }

        self.login_type = 2
        self.login_at = None
        self.logout_at = None
        self.need_login_tags=['name="login"',
                              '<input id="LoginName" name="UserID" type="text" value="" placeholder="请输入用户名" />']
        self.resume_tags=['个人信息', '求职意向']
        self.login_success_tag=[]

        # self.cookie_fpath=cookie_fpath
        self.inuse_taskfpath=''

        #用于记录执行号段任务的参数，起始/结束/当前
        self.maxsleeptime = 4
        self.area_list=['530','538','763','765']
        self.now_time = datetime.datetime.now()
        self.yes_time = self.now_time + datetime.timedelta(days=-3)
        self.yester_time = self.yes_time.strftime('%Y-%m-%d').replace('20','')

        username1 = acc.uni_user()
        if username1:
            self.username = username1
            print self.username
            logging.info('cjol buy select username is {}'.format(self.username))
            self.headers['Cookie'] = acc.redis_ck_get(self.username)
        else:
            logging.error('no avail login cookie for cjol')
            # print '没有已经登陆的 cjol cookie文件'
            quit()
        print 'id num is {}'.format(id_number)
        print 'position is {}'.format(position)
        logging.info('trying to buy id {}, position is {}'.format(self.id_number, self.position))


    def isResume_chk(self,html):
        '''功能描述：检查返回内容是否为合格简历'''
        try:
            flag = -1
            if html:
                if html.find('无法查看') > -1:
                    flag = 2
                    self.save_error_file(html)
                if html.find('该求职上传了附件简历,查看联系方式后可下载') > -1:
                    flag = 3
                if html.find('查看的简历数量已经超过限制') > -1:
                    flag = 4
                    self.save_error_file(html)
                if html.find('输入验证码才能继续后续的操作') > -1:
                    flag = 6
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
                    chk_url = r'http://rdsearch.zhaopin.com/Home/'
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
            # print self.cookie_fpath
            self.refer = "http://rd.zhaopin.com/resumepreview/resume/viewone" \
                         "/2/{}_1_1?searchresume=1".format(self.id_number)
            self.headers['Referer']=self.refer
            print self.refer
            self.headers['Host'] = 'rd.zhaopin.com'
            # self.headers['Origin'] = 'http://rms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
            position = self.position
            # cookie_fpath = self.cookie_fpath
            # if not cookie_fpath:
            #     logging.debug('load cookie error for position %s' % position)
            #     print 'cookie path no exist!'
            #     exit()
            # if os.path.exists(cookie_fpath):
            #     self.load_cookie(cookie_fpath)
            # else:
            #     logging.debug('cookie file %s not exit.' % cookie_fpath)
            #     print 'cookie path no exist!'
            #     exit()
            s = requests.Session()
            s.trust_env = False
            s.headers = self.headers
            proxies = {
                  'http': 'http://183.131.144.102:8081',
                  'https': 'http://183.131.144.102:8081',
                }

            debug = self.debug

            if not self.debug:
                # 解析 resumeName
                url_0 = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/{}' \
                        '_1_1?searchresume=1#'.format(self.id_number)
                html_0 = s.get(url_0, proxies=proxies).text
                # html_0 = self.url_get(url_0)
                soupid = BeautifulSoup(html_0,"html5lib")
                resumeName = soupid.find('strong', {'id':"resumeName"}).get_text()
                print type(resumeName)
                resumeName = urllib.quote(resumeName.encode('utf-8'))
                print resumeName

                ###################################
                # if bankid != -1:  #todo 改为不等号
                #     print 'already download this id'
                #     #quit()
                ### 购买简历 TODO
                db = sqlite3.connect(buy_database_path)
                cursor = db.cursor()
                sql_cr = ''' create table If not EXISTS zhilian
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
                sql_se = """ select id_num,nam,phone,buy_user,email,add_time from zhilian WHERE id_num='{}' """.format(self.id_number)
                cursor.execute(sql_se)
                data = cursor.fetchall()
                db.close()
                # 缓存一份在 sqlite 防止重复购买， debug的时候可以去掉，重复购买已购买简历
                if len(data) > 0:
                    idnum, name, phone, buy_user, email, add_time = data[0]
                    print 'already down this id {} and {} account is {}, buy_time is {}'.format(self.id_number, self.module_name, buy_user, add_time)
                    print "buy_resume_done,{},{},{}".format(name, phone, email)
                    quit()

                # 先解析出 公共收藏夹的 id favoriteID
                url_fav = r"http://rd.zhaopin.com/resumepreview/resume/_Download?extID={}&resumeVersion=1&language=1&dType=undefined".format(str(self.id_number))
                html_f = s.get(url_fav, proxies=proxies).text
                soup_f = BeautifulSoup(html_f, 'html.parser')
                fav_id = soup_f.find('option').get('value')

                url_buy = r"http://rd.zhaopin.com/resumepreview/resume/DownloadResume"
                payload = {
                        'extID': str(self.id_number),
                        'versionNumber': '1',
                        'favoriteID': fav_id,
                        'resumeName': resumeName,
                        'dType': '0',
                          }
                # post_data = urllib.urlencode(payload)
                #print post_data
                html = s.post(url_buy, data=payload, proxies=proxies).text
                # html = self.url_post(url_buy, post_data)
                print html.encode('utf-8')
                html_json = json.loads(html)
                code = int(html_json["ErrorCode"])
                msg = html_json["Message"]
                print '招聘渠道错误代码', code
                print '招聘渠道返回信息', msg.encode('utf-8')
                if code != 0:
                    print '购买失败'
                    print 'buy resume error, and error msg is {}'.format(msg)
                    logging.error('buy resume error, and error msg is {}'.format(msg))
                    quit()
                else:
                    print 'zhilian id {} 购买成功'.format(self.id_number)
                    logging.info('zhilian id {}, buy succeed'.format(self.id_number))

                #print chardet.detect(html)
                #print html.encode('GB2312', 'ignore')

                # url_r = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/{}' \
                #         '_1_1?searchresume=1#'.format(self.id_number)
                # payload = {
                #         'JobSeekerID': str(self.id_number),
                #         'Fn':'resume',
                #         'bankid': bankid,
                #         'Lang':'CN',
                #           }
                # post_data = urllib.urlencode(payload)
                # html_r = self.url_get(url_0)
                # print html_r
                print self.id_number
            else:
                print "----- debug down buy"
                #print html
                ### TODO 检查返回的关键词中如果没有"成功下载"这几个字就标示没有下载成功, 出错了直接打印错误信息

                ### 购买完简历接着下载带联系方式等的简历: TODO 这种方式下载简历存在之前个别账户无法拼 URL 访问的潜在问题
            if not self.debug:
                req_count = 0
                r = Rdsreport()
                while req_count < 3:
                    req_count+=1
                    try:
                        url_1 = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/{}' \
                                '_1_1?searchresume=1#'.format(self.id_number)
                        urlhtml = s.get(url_1, proxies=proxies).text
                        # urlhtml = self.url_get(url_1)
                        isResume = self.isResume_chk(urlhtml)
                        prefixid = 'z_' + str(self.id_number)
                        addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if isResume == -2:
                            req_count =0
                        elif isResume == -1:
                            req_count =3
                        elif isResume == 4:
                            txt_title = self.module_name + 'max limit!!'
                            txt_msg = self.module_name + '<br>cookie path'+ self.cookie_fpath+ '<br>'+'current:id_number:'+ str(self.id_number) + '<br>' + urlhtml
                            self.send_mails(txt_title, txt_msg, 0)
                            # logging.info('waring! More than the largest number at %s ' % str(x))
                            time.sleep(6000*2)
                        elif isResume == 1:
                            if self.save_resume(str(self.id_number), urlhtml):                # 默认id长度为23
                                data_total_add(self.module_name)               # 写入记录到数据库
                                try:
                                    es_redis = r.es_check(prefixid)
                                    if es_redis == 0:
                                        data_back = ExtractSegInsert.fetch_do123(urlhtml.encode('uft-8'), 'zhilian', 1)
                                    elif es_redis == 1:
                                        data_back = ExtractSegInsert.fetch_do123(urlhtml.encode('utf-8'),'zhilian', -1)
                                    resume = data_back[0]
                                    ex_result = data_back[1]
                                    print ex_result,resume
                                    if ex_result == 1:
                                        r.tranredis('zhilian_seg', 1, ext1='insert', ext2='ok')
                                        r.es_add(prefixid, addtime, 1)
                                    elif ex_result == -1:
                                        r.tranredis('zhilian_seg', 1, ext1='update', ext2='ok')
                                        r.es_add(prefixid, addtime, 1)
                                    elif ex_result == -4:
                                        r.tranredis('zhilian_seg', 1, ext1='update', ext2='search_err')
                                        r.es_add(prefixid, addtime, 1)
                                    elif ex_result == 0:
                                        r.tranredis('zhilian_seg', 1, ext1='insert', ext2='not_insert')
                                        r.es_add(prefixid, addtime, 0)
                                    elif ex_result == -2:
                                        r.tranredis('zhilian_seg', 1, ext1='', ext2='parse_err')
                                        r.es_add(prefixid, addtime, 0)
                                        error_path = os.path.join('error/zhilian', str(self.id_number)+'.html')
                                        with open(error_path, 'w+') as f:
                                            f.write(urlhtml)
                                    elif ex_result == -3:
                                        r.tranredis('zhilian_seg', 1, ext1='', ext2='source_err')
                                        r.es_add(prefixid, addtime, 0)
                                    elif ex_result == -5:
                                        r.tranredis('zhilian_seg', 1, ext1='', ext2='operate_err')
                                        r.es_add(prefixid, addtime, 0)
                                except Exception, e:
                                    print traceback.format_exc()
                                    logging.warning('zhilian resume_id %s extractseginsert fail error msg is %s' %(str(self.id_number), e))
                            else:
                                pass
                            break
                        elif isResume == 2:
                            logging.info('resume_id %s is secrect resume.' % str(self.id_number))
                            break
                        elif isResume == 3:
                            logging.info('resume_id %s is removed by system.'% str(self.id_number))
                            break
                        elif isResume == 5:
                            logging.info('too more busy action and have a rest')
                            time.sleep(20*60)
                            break
                        elif isResume == 6:
                            txt_title = self.module_name + '请求量过大导致系统无法处理您的请求，您需要输入验证码才能继续后续的操作'
                            txt_msg = self.module_name + '<br>cookie path'+ self.cookie_fpath+ '<br>'+'当前抓取id_number:'+ str(self.id_number) + '<br>' + urlhtml
                            self.send_mails(txt_title, txt_msg, 0)
                            # logging.info('waring!requst too much,Please enter the verification code %s ' % str(x))
                            req_count = 0
                            time.sleep(10*100)
                    except Exception,e:
                        logging.debug('get %s resume error and msg is %s' % (str(self.id_number),str(e)))

            else:
                print "----- debug down bought resume"

            ### 读取本地文件调试
            if self.debug:
                logging.info('debug zhilian local file')
                with open("22zl.html") as f:
                    urlhtml = f.read()
            #print html
            ### TODO 需要检查下文件是否正确
            # x = self.id_number
            # self.save_resume(str(x),html)

            ### 最终操作成功返回解析出来的 姓名,电话,Email

            soup = BeautifulSoup(urlhtml,'html.parser')     #解析出尾段对应的hiduserid
            # 姓名
            name = ''
            phone = ''
            email = ''
            try:
                name = soup.find('div', {'id': 'userName'}).get_text().strip()
            except:
                logging.error('parser zhilian name error')
                pass
            # print name[0].string.encode('utf-8')
            print name.encode('utf-8')
            try:
                phone = soup.select('em')[0].get_text()
            except:
                logging.error('parser zhilian phone error')
                pass
            try:
                email = soup.select('em')[1].get_text()
            except:
                logging.error('parser zhilian email error')
                pass
            try:
                sql = """insert into zhilian (id_num, nam, phone, email, buy_user) VALUES ('{}', '{}', '{}', '{}','{}') """\
                    .format(self.id_number, name, phone, email, self.username)
                db = sqlite3.connect(buy_database_path)
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
                db.close()
            except Exception, e:
                logging.error('insert sqlite3 error msg is {}'.format(str(e)))
            logging.info("buy_resume_done,{},{},{}".format(name, phone, email))
            print "buy_resume_done,{},{},{}".format(name, phone, email) #% (name, phone, email)


        except Exception,e:
            print traceback.format_exc()
            logging.debug('error msg is %s' % str(e))
            return False


### 调试: python main.py  cjoldown gz 300584521 debug
if __name__ == '__main__':
    print 'test...'
    a=mainfetch('bj',"JM093009769R90250001000")
    # a=mainfetch('gz',"JM623078170R90250000000")
    a.run_work()




