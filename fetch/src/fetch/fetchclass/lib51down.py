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
import buy2talent, common
from extract_seg_insert import ExtractSegInsert
from redispipe import *


class down51job(BaseFetch):
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
        acc = libaccount.Manage(source='51job', option='buy', location=ppp)
        # init other log
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['loggers'][""]['handlers'] = ["file", "stream", "buy", "error"]
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

        self.resume_tags=['<div id="divResume"><style>','简历编号', '简历信息']
        self.login_success_tag=[]

        self.adviser_user = adviser_user
        self.id_number=id_number
        self.position = position
        self.inuse_taskfpath=''

        #用于记录执行号段任务的参数，起始/结束/当前
        self.start_num=0
        self.end_num=0
        self.current_num=self.start_num
        self.maxsleeptime = 5
        self.logger = common.log_init(__name__, '51buy2.log')
        username1 = acc.uni_user()
        self.logger.info('select username is {}'.format(username1))
        self.has_cookie = True
        if username1:
            self.username = username1
            logging.info('cjol buy select username is {}'.format(self.username))
            self.headers['Cookie'] = acc.redis_ck_get(self.username)
        else:
            logging.error('no avail login cookie for 51down')
            self.send_mails('Warining, no account for 51down', 'no avail login cookie for 51down')
            print '没有已经登陆的 51job cookie文件'
            self.has_cookie = False
            # quit()  # 这里不退出，在runwork那里才 return something
        print 'id num is {}'.format(id_number)
        print 'position is {}'.format(position)
        logging.info('trying to buy id {}, position is {}'.format(self.id_number, self.position))


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

    def resume_link(self):
        """某些51 的还是需要带上简历页面后面的加密串才可以访问到简历"""
        try:
            url = 'http://ehire.51job.com/Candidate/SearchResumeIndex.aspx'
            html = self.url_get(url)
            # soup = BeautifulSoup(html, 'html.parser')
            # hidSearchID = "2,3,6,23,8,1,4,5,25,2,3,6,23" # soup.find('input', {'id': 'hidSearchID'}).get('value')
            # VIEWSTATE = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
            hidSearchID = re.search('hidSearchID" value=.*"', html).group()
            hidSearchID = hidSearchID.replace('hidSearchID" value="', '')[:-1]
            VIEWSTATE = re.search('__VIEWSTATE" value=.*"', html).group()
            VIEWSTATE = VIEWSTATE.replace('__VIEWSTATE" value="', '')[:-1]
            post_dict = {
                "txtUserID": self.id_number,
                "DpSearchList": "",
                "WORKFUN1$Text": "最多只允许选择3个项目",
                "WORKFUN1$Value": "",
                "KEYWORD": "---多关键字用空格隔开，请勿输入姓名、联系方式---",
                "AREA$Value": "",
                "WorkYearFrom": "0",
                "WorkYearTo": "99",
                "TopDegreeFrom": "",
                "TopDegreeTo": "",
                "LASTMODIFYSEL": "5",
                "WORKINDUSTRY1$Text": "最多只允许选择3个项目",
                "WORKINDUSTRY1$Value": "",
                "SEX": "99",
                "JOBSTATUS": "99",
                "hidSearchID": hidSearchID,
                "hidWhere": "",
                "hidValue": "ResumeID#{}".format(self.id_number),
                "hidTable": "",
                "hidSearchNameID": "",
                "hidPostBackFunType": "",
                "hidChkedRelFunType": "",
                "hidChkedExpectJobArea": "",
                "hidChkedKeyWordType": "0",
                "hidNeedRecommendFunType": "",
                "hidIsFirstLoadJobDiv": "1",
                "txtSearchName": "",
                "ddlSendCycle": "1",
                "ddlEndDate": "7",
                "ddlSendNum": "10",
                "txtSendEmail": "",
                "txtJobName": "",
                "showGuide": "1",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__LASTFOCUS": "",
                "__VIEWSTATE": VIEWSTATE
            }
            url2 = 'http://ehire.51job.com/Candidate/SearchResume.aspx'
            html2 = self.url_post(url2, postDict=urllib.urlencode(post_dict))
            soup2 = BeautifulSoup(html2, 'html.parser')
            re_link = soup2.find('span', {'class': 'SearchR', 'id': 'spanB{}'.format(self.id_number)}).a.get('href')
            re_link2 = 'http://ehire.51job.com' + re_link
            # print re_link2
            logging.info('resume link is {}'.format(re_link2))
            return re_link2
        except Exception as e:
            logging.error('error', exc_info=True)


    def resume_link_new(self):
        """某些51 的还是需要带上简历页面后面的加密串才可以访问到简历, 新的搜索页"""
        try:
            url = 'http://ehire.51job.com/Candidate/SearchResumeIndex.aspx'
            html = self.url_get(url)
            if html.find(u'切换到旧版</a>') < 0:
                self.logger.info('get resume link from old search page')
                re_link2 = self.resume_link()
            else:
                # soup = BeautifulSoup(html, 'html.parser')
                # hidSearchID = "2,3,6,23,8,1,4,5,25,2,3,6,23" # soup.find('input', {'id': 'hidSearchID'}).get('value')
                # VIEWSTATE = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
                # hidSearchID = re.search('hidSearchID" value=.*"', html).group()
                # hidSearchID = hidSearchID.replace('hidSearchID" value="', '')[:-1]
                self.logger.info('try to get resume link via new search page')
                VIEWSTATE = re.search('__VIEWSTATE" value=.*"', html).group()
                VIEWSTATE = VIEWSTATE.replace('__VIEWSTATE" value="', '')[:-1]
                post_dict = {
                    "__VIEWSTATE": VIEWSTATE,
                    "search_area_hid": "",
                    "sex_ch": "99|不限",
                    "sex_en": "99|Unlimited",
                    "send_cycle": "1",
                    "send_time": "7",
                    "send_sum": "10",
                    "feedback": "on",
                    "hidWhere": "",
                    "searchValueHid": "{}##0##########99##########1#0#".format(self.id_number),
                    "showGuide": "",
                }
                url2 = 'http://ehire.51job.com/Candidate/SearchResumeNew.aspx'
                html2 = self.url_post(url2, postDict=urllib.urlencode(post_dict))
                soup2 = BeautifulSoup(html2, 'html.parser')
                re_link = soup2.find('span', {'id': 'spanB{}'.format(self.id_number)}).a.get('href')
                re_link2 = 'http://ehire.51job.com' + re_link
                # print re_link2
                logging.info('resume link is {}'.format(re_link2))
            return re_link2
        except Exception as e:
            logging.error('error', exc_info=True)


    ### 调试: python main.py  down51 gz 300584521 debug
    def run_down(self):
        '''功能描述,执行简历下载'''
        ### TODO 原来的程序构造函数和这里分别有载入 cookie , 感觉是重复的? 不加这里好像又有问题
        # 选取合适的 cookie 文件
        try:
            if not self.has_cookie:
                # 没有可用  cookie  在这里直接退出
                return json.dumps({'status': 'error', 'msg': 'no avail cookie for 51job',
                                       'time': str(datetime.datetime.now())})
            seged_dict = {}
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
                    return json.dumps({'name': name, 'phone': phone, 'email': email, 'id': self.id_number,
                                       'status': 'already', 'time': add_time, 'user': buy_user})

                # 购买之后的 简历页面结构不一样，导致解析可能出错，所以现在购买之前先把简历下载下来，
                # 然后入库，主要是 要解析后的字典，入库成不成功不影响后面的操作。
                url_ori = self.resume_link_new()
                if not self.debug:
                    req_count = 0
                    while req_count < 3:
                        req_count += 1
                        try:
                            logging.info('begin to get resume %s from internet' % str(self.id_number))
                            html = self.url_get(url_ori)
                            isResume = self.isResume_chk(html)
                            print isResume
                            if isResume == -2:
                                logging.info('error page is %s' % str(self.id_number))
                                break
                            elif isResume == -1:
                                req_count = 3
                            elif isResume == 0:
                                # self.login()
                                # req_count = 0
								pass
                            elif isResume == 1:
                                self.save_resume(str(self.id_number), html)
                                try:
                                    prefixid = 'wu_' + str(self.id_number)
                                    addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    r = self.rp
                                    r.rcheck(prefixid, addtime)
                                    es_redis = r.es_check(prefixid)
                                    if es_redis == 0:
                                        data_back = ExtractSegInsert.fetch_do123(html, '51job', 1)
                                    elif es_redis == 1:
                                        data_back = ExtractSegInsert.fetch_do123(html, '51job', -1)
                                    resume = data_back[0]
                                    ex_result = data_back[1]
                                    seged_dict = data_back[2]
                                    # print ex_result, resume
                                    if ex_result == 1:
                                        r.tranredis('51search_seg', 1, ext1='insert', ext2='ok')
                                        r.es_add(prefixid, addtime, 1)
                                    elif ex_result == -1:
                                        r.tranredis('51search_seg', 1, ext1='update', ext2='ok')
                                        r.es_add(prefixid, addtime, 1)
                                    elif ex_result == -4:
                                        r.tranredis('51search_seg', 1, ext1='update',
                                                    ext2='search_err')
                                        r.es_add(prefixid, addtime, 1)
                                    elif ex_result == 0:
                                        r.tranredis('51search_seg', 1, ext1='insert',
                                                    ext2='not_insert')
                                        r.es_add(prefixid, addtime, 0)
                                    elif ex_result == -2:
                                        r.tranredis('51search_seg', 1, ext1='',
                                                    ext2='parse_err')
                                        r.es_add(prefixid, addtime, 0)
                                        error_path = os.path.join('error/51search',
                                                                  str(self.id_number) + '.html')
                                        with open(error_path, 'w+') as f:
                                            f.write(html)
                                    elif ex_result == -3:
                                        r.tranredis('51search_seg', 1, ext1='',
                                                    ext2='source_err')
                                        r.es_add(prefixid, addtime, 0)
                                    elif ex_result == -5:
                                        r.tranredis('51search_seg', 1, ext1='',
                                                    ext2='operate_err')
                                        r.es_add(prefixid, addtime, 0)
                                except Exception, e:
                                    logging.warning(
                                        '51buy resume_id %s extractseginsert fail error msg is %s' % (
                                        self.id_number, e), exc_info=True)
                                    self.logger.warning(
                                        '51buy resume_id %s extractseginsert fail error msg is %s' % (
                                        self.id_number, e), exc_info=True)
                                break
                            elif isResume == 2:
                                logging.info('resume_id %s is secrect resume.' % str(self.id_number))
                                self.logger.info('resume_id %s is secrect resume.' % str(self.id_number))
                                break
                            elif isResume == 3:
                                logging.info('resume_id %s is removed by system.' % str(self.id_number))
                                self.logger.info('resume_id %s is removed by system.' % str(self.id_number))
                                self.logger.info('remved by system url is {}'.format(url))
                                break
                            elif isResume == 4:
                                logging.info('too more busy action and have a rest')
                                self.logger.info('too more busy action and have a rest')
                                time.sleep(20 * 60)
                                break
                        except Exception, e:
                            logging.debug('get %s resume error and msg ' % str(self.id_number))
                            self.logger.debug('get %s resume error and msg ' % str(self.id_number))
                else:
                    print "----- debug down bought resume"

                # 购买相关代码
                post_data = 'doType=SearchToCompanyHr&userId=%s&strWhere=' % str(self.id_number)
                url = r"http://ehire.51job.com/Ajax/Resume/GlobalDownload.aspx"
                html = self.url_post(url, post_data)
                print self.id_number
                print html
                if html.find(u'成功下载1份') < 0 and html.find(u'简历已在公司人才夹中') < 0:
                    print '购买失败，购买返回信息如上'
                    logging.critical('51 buy fail, and buy error msg is {}'.format(html))
                    return json.dumps({'status': 'error', 'msg': 'buy error and msg from 51job {}'.format(html),
                                       'time': str(datetime.datetime.now()), 'user': self.username})
                else:
                    print '51job id {}, 购买成功'.format(self.id_number)
                    logging.info('51 user{} id {} buy success'.format(self.username, self.id_number))
                # if html.find('登录已失效') > 0:


            else:
                print "----- debug down buy"
                #print html
                ### TODO 检查返回的关键词中如果没有"成功下载"这几个字就标示没有下载成功, 出错了直接打印错误信息

                ### 购买完简历接着下载带联系方式等的简历: TODO 这种方式下载简历存在之前个别账户无法拼 URL 访问的潜在问题


            ### 读取本地文件调试
            if self.debug:
                logging.info('51 bug debug')
                html = open("buy.html").read()
            # print html
            ### TODO 需要检查下文件是否正确
            ## 重新访问 简历链接 得到购买后的页面

            html = self.url_get(url_ori)
            self.save_resume(str(self.id_number),html)

            ### 最终操作成功返回解析出来的 姓名,电话,Email

            soup = BeautifulSoup(html,'html.parser')     #解析出尾段对应的hiduserid
            # 姓名
            try:
                name = soup.select("title")
                name = name[0].string.encode('utf-8').strip()
            except:
                name = ''
                logging.error('parser 51job name error')
                self.logger.error('parser 51job name error')
                pass

            # tds = soup.select("#divResume table table table tr td")
            # phone = tds[7].string.encode('utf-8').strip()
            # email = tds[9].string.encode('utf-8').strip()
            try:
                phone = re.search('1\d{10}（', html).group()[:11]
            except:
                logging.error('parser 51job phone error')
                self.logger.error('parser 51job phone error', exc_info=True)
                phone = ''
            try:
                email = re.search("[\w.]+@[\w.]+", html).group()
            except:
                logging.error('parser 51job email error')
                self.logger.error('parser 51job email error', exc_info=True)
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
            self.logger.info("buy_resume_done,%s,%s,%s" % (name, phone, email))
            print "buy_resume_done,%s,%s,%s" % (name, phone, email)
            message = {'name': name, 'phone': phone, 'email': email, 'id': self.id_number,
                       'status': 'ok', 'time': str(datetime.datetime.now()), 'user': self.username}
            b2t = buy2talent.BTalent('51job', self.id_number, phone, name, email, seged_dict)
            if seged_dict == {}:
                message['ps'] = 'error cannot down resume or parse resume error, please complete resume manually'
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
            logging.error('error msg is %s' % str(e))
            self.logger.error('error msg is %s' % str(e))
            self.send_mails('warning 51down err', '51down id {} error msg is {}'.format(self.id_number, e))
            return json.dumps({'status': 'python error', 'msg': e, 'time': str(datetime.datetime.now()),
                               'user': self.username})


if __name__ == '__main__':
    a = down51job(id_number='347209620', position='bj' )
    #a.resume_link()
    a.run_down()
