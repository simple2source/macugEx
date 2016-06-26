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
import buy2talent


class mainfetch(BaseFetch):
    def __init__(self,  position = '', id_number='', adviser_user=''):
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
        self.rp = Rdsreport()  # 将这个放在前面，避免 redispipe 初始化的时候，将logger 的保存位置改到别的地方
        acc = libaccount.Manage(source='zhilian', option='buy', location=ppp)
        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['loggers'][""]['handlers'] = ["file", "stream", "buy", "error"]
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')

        self.adviser_user = adviser_user
        self.id_number=id_number
        self.position = position

        self.host=r'rd.zhaopin.com'
        self.domain='zhaopin.com'
        self.module_name='zhiliandown'
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
        self.logger = common.log_init(__name__, 'zlbuy2.log')
        username1 = acc.uni_user()
        self.logger.info('get buy username is {}'.format(username1))
        self.has_cookie = True
        if username1:
            self.username = username1
            logging.info('zhilian buy select username is {}'.format(self.username))
            self.logger.info('zhilian buy select username is {}'.format(self.username))
            self.headers['Cookie'] = acc.redis_ck_get(self.username)
        else:
            logging.error('no avail login cookie for zldown')
            self.logger.error('no avail login cookie for zldown')
            self.send_mails('Warining, no account for zldown', 'no avail login cookie for zldown')
            print '没有已经登陆的 zldown cookie文件'
            self.has_cookie = False
            # quit()  # 这里不退出，在runwork那里才 return something
        print 'id num is {}'.format(id_number)
        print 'position is {}'.format(position)
        logging.info('trying to buy id {}, position is {}'.format(self.id_number, self.position))
        self.logger.info('trying to buy id {}, position is {}'.format(self.id_number, self.position))


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
            self.logger.debug('error msg is %s'% str(e))
            return -1


    def resume_link(self):
        """通过搜索页面得到简历的链接（现在智联的简历链接需要带小尾巴）"""
        self.refer = "http://rdsearch.zhaopin.com/Home/SearchByResumeId"
        self.headers['Host'] = "rdsearch.zhaopin.com"
        self.headers['Referer'] = self.refer
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) A' \
                                     'ppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
        s = requests.Session()
        s.trust_env = False
        s.headers = self.headers
        proxies = {
            'http': 'http://10.4.16.39:8888',
            'https': 'http://10.4.16.39:8888',
        }
        resume_url = None
        url = 'http://rdsearch.zhaopin.com/Home/ResultForRe'\
                  'sumeId?SF_1_1_24={}&orderBy=DATE_MODIFIED,1&SF_1_1_27=0&exclude=1'.format(self.id_number)
        try:
            r = s.get(url, proxies=proxies)

            soup = BeautifulSoup(r.text, 'html.parser')
            soup2 = soup.find_all('a', {'name': 'resumeLink'})
            for i in soup2:
                if i.get('tag') == str(self.id_number) + '_1':
                    t = i.get('t')
                    k = i.get('k')
                    resume_url = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/{}_1_1?' \
                                 'searchresume=1&t={}&k={}'.format(self.id_number, t, k)
            return resume_url
        except Exception as e:
            logging.error('get id {} tmp url error error msg is {}'.format(self.id_number, e), exc_info=True)
            self.logger.error('get id {} tmp url error error msg is {}'.format(self.id_number, e), exc_info=True)
            return None

    def run_work(self):
        '''功能描述：执行任务主工作入口函数'''
        try:
            if not self.has_cookie:
                # 没有可用  cookie  在这里直接退出
                return json.dumps({'status': 'error', 'msg': 'no avail cookie for zhilian',
                                       'time': str(datetime.datetime.now())})
            seged_dict = {}
            # print self.cookie_fpath
            self.refer = "http://rdsearch.zhaopin.com/home/RedirectToRd/{}_1_1?searchresume=1".format(self.id_number)
            self.headers['Referer']=self.refer
            # print self.refer
            self.headers['Host'] = 'rd.zhaopin.com'
            # self.headers['Origin'] = 'http://rms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
            self.headers['Origin'] = 'http://rdsearch.zhaopin.com'
            position = self.position
            s = requests.Session()
            s.trust_env = False
            s.headers = self.headers
            proxies = {
                  'http': 'http://10.4.16.39:8888',
                  'https': 'http://10.4.16.39:8888',
                }

            debug = self.debug

            if not self.debug:
                # 解析 resumeName
                url_0 = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/{}' \
                        '_1_1?searchresume=1#'.format(self.id_number)
                tmp_url = self.resume_link()
                if tmp_url is None:
                    logging.critical('get id_number zhilian url error')
                    self.logger.critical('get id_number zhilian url error')
                    # quit()
                    # 没有找到可用的 带加密串的 智联简历链接，这里也退出
                    return json.dumps({'status': 'error', 'msg': 'cannot find tmp resume url for zhilian',
                                       'time': str(datetime.datetime.now())})
                html_0 = s.get(tmp_url, proxies=proxies).text
                # html_0 = self.url_get(url_0)
                soupid = BeautifulSoup(html_0,"html.parser")
                resumeName = soupid.find('strong', {'id':"resumeName"}).get_text()
                print type(resumeName)
                resumeName = urllib.quote(resumeName.encode('utf-8'))
                print resumeName
                # quit()

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
                    return json.dumps({'name': name, 'phone': phone, 'email': email, 'id': self.id_number,
                                      'status': 'already', 'time': add_time, 'user': buy_user})

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
                    self.logger.error('buy resume error, and error msg is {}'.format(msg))
                    return json.dumps({'status': 'error', 'msg': 'buy error and msg from zhilian {}'.format(html),
                                       'time': str(datetime.datetime.now()), 'user': self.username})
                else:
                    print 'zhilian id {} 购买成功'.format(self.id_number)
                    logging.info('zhilian user {} id {}, buy succeed'.format(self.username, self.id_number))
                    self.logger.info('zhilian user {} id {}, buy succeed'.format(self.username, self.id_number))

                print self.id_number
            else:
                print "----- debug down buy"
                #print html
                ### TODO 检查返回的关键词中如果没有"成功下载"这几个字就标示没有下载成功, 出错了直接打印错误信息

                ### 购买完简历接着下载带联系方式等的简历:
            if not self.debug:
                req_count = 0
                r = self.rp
                while req_count < 3:
                    req_count+=1
                    try:
                        url_1 = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/{}' \
                                '_1_1?searchresume=1#'.format(self.id_number)
                        urlhtml = s.get(tmp_url, proxies=proxies).text
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
                                    r.rcheck(prefixid, addtime)
                                    es_redis = r.es_check(prefixid)
                                    if es_redis == 0:
                                        data_back = ExtractSegInsert.fetch_do123(urlhtml.encode('utf-8'), 'zhilian', 1)
                                    elif es_redis == 1:
                                        data_back = ExtractSegInsert.fetch_do123(urlhtml.encode('utf-8'),'zhilian', -1)
                                    resume = data_back[0]
                                    ex_result = data_back[1]
                                    seged_dict = data_back[2]
                                    # print ex_result,resume
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
                                    self.logger.warning('zhilian resume_id %s extractseginsert fail error msg is %s' %(str(self.id_number), e))
                            else:
                                pass
                            break
                        elif isResume == 2:
                            logging.info('resume_id %s is secrect resume.' % str(self.id_number))
                            self.logger.info('resume_id %s is secrect resume.' % str(self.id_number))
                            break
                        elif isResume == 3:
                            logging.info('resume_id %s is removed by system.'% str(self.id_number))
                            self.logger.info('resume_id %s is removed by system.'% str(self.id_number))
                            break
                        elif isResume == 5:
                            logging.info('too more busy action and have a rest')
                            self.logger.info('too more busy action and have a rest')
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
                        self.logger.debug('get %s resume error and msg is %s' % (str(self.id_number),str(e)))

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
                self.logger.error('parser zhilian name error')
                pass
            # print name[0].string.encode('utf-8')
            print name.encode('utf-8')
            try:
                phone = soup.select('em')[0].get_text()
            except:
                logging.error('parser zhilian phone error')
                self.logger.error('parser zhilian phone error')
                pass
            try:
                email = soup.select('em')[1].get_text()
            except:
                logging.error('parser zhilian email error')
                self.logger.error('parser zhilian email error')
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
                self.logger.error('insert sqlite3 error msg is {}'.format(str(e)))
            logging.info("buy_resume_done,{},{},{}".format(name, phone, email))
            self.logger.info("buy_resume_done,{},{},{}".format(name, phone, email))
            print "buy_resume_done,{},{},{}".format(name, phone, email) #% (name, phone, email)
            message = {'name': name, 'phone': phone, 'email': email, 'id': self.id_number,
                       'status': 'ok', 'time': str(datetime.datetime.now()), 'user': self.username}
            b2t = buy2talent.BTalent('zhilian', self.id_number, phone, name, email, seged_dict)
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
            print traceback.format_exc()
            logging.debug('error msg is %s' % str(e))
            self.send_mails('warning zldown err', 'zldown id {} error, err msg is {}'.format(self.id_number, e))
            return json.dumps({'status': 'python error', 'msg': e, 'time': str(datetime.datetime.now()),
                               'user': self.username})

### 调试: python main.py  cjoldown gz 300584521 debug
if __name__ == '__main__':
    print 'test...'
    a=mainfetch('gz',"z_JM332695108R90250004000")
    # a=mainfetch('gz',"JM623078170R90250000000")
    a.run_work()




