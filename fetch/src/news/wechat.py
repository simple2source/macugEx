# coding: utf-8

from common import *
from bs4 import BeautifulSoup
import chardet
import time
import json, os, string, datetime
import MySQLdb
import common, logging
import logging.config
import HTMLParser, sys
reload(sys)
sys.setdefaultencoding('utf8')

class WeChat():
    def __init__(self):
        print '_________________'
        # self.sql_config = {
        #     'host': "localhost",
        #     'user': "testuser",
        #     'passwd': "",
        #     'db': 'tuike',
        #     'charset': 'utf8',
        # }
        self.sql_config = {
            'host': "10.4.14.233",
            'user': "tuike",
            'passwd': "sv8VW6VhmxUZjTrU",
            'db': 'tuike',
            'charset': 'utf8',
        }
        self.url = 'http://weixin.sogou.com/'
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            # 'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Host':"weixin.sogou.com",
            # 'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
        }
        self.s = requests.Session()
        self.s.headers = self.headers
        # self.s.get(self.url)
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
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'wechat.log')
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha, start wechat')
        self.ck_mk = []
        self.mk_ck_str2()
        # quit()
        self.rand_ck3()
        self.rand_ua()
        requests.packages.urllib3.disable_warnings()
        # self.r = redis.StrictRedis()
        # init other log


    def mk_ck_str(self):
        """ 初始化的时候，先访问搜狗10次，得到10个有效的cookie，设定cookie不是办法。仅在IP没有被封情况下可用"""
        url = "http://weixin.sogou.com"
        for i in xrange(0, 10):  # 生成10个新的cookie
            self.s = requests.Session()
            self.s.headers['Host'] = 'weixin.sogou.com'
            self.s.get('http://weixin.sogou.com/')
            self.s.headers['Host'] = 'pb.sogou.com'
            self.s.headers['Referer'] = 'http://weixin.sogou.com/'
            r3 = self.s.get('http://pb.sogou.com/pb.js')
            print r3.headers, 99999999999999999

            ck = requests.utils.dict_from_cookiejar(self.s.cookies)
            cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()])
            print ck
            print cookie_string
            query = ''.join(random.choice(string.lowercase) for i in range(random.choice(range(4, 8))))
            print query
            url2 = "http://weixin.sogou.com/weixin?type=1&query={}&ie=utf8".format(query)
            self.s.headers = self.headers
            self.s.headers['Referer'] = 'http://weixin.sogou.com'
            self.s.headers['Host'] = 'www.sogou.com'
            r1 = self.s.get('http://www.sogou.com/websearch/features/year.jsp')
            print r1.headers, 99999999999999999999

            ck = requests.utils.dict_from_cookiejar(self.s.cookies)
            print ck
            cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()])
            print cookie_string


            r2 = self.s.get('http://www.sogou.com/sug/css/m3.min.v.2.css')
            print r2.headers, 9999999999999999999999
            ck = requests.utils.dict_from_cookiejar(self.s.cookies)
            cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()])
            # self.rand_ua()
            print '++++++++'
            self.s.headers['Referer'] = 'http://weixin.sogou.com/'
            self.s.headers['Host'] = 'weixin.sogou.com/'
            r = self.s.get(url2)
            print r.headers, 99999999999999
            # print self.s.headers
            # print self.s.cookies
            ck = requests.utils.dict_from_cookiejar(self.s.cookies)
            cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()])
            print cookie_string
            self.ck_mk.append(cookie_string)
            print self.ck_mk
            if r.url.find('spider') > 0:
                print r.url
            quit()
            rand_sleep(20, 5)
        return True


    def mk_ck_str2(self):
        """ 初始化的时候，先访问搜狗10次，得到10个有效的cookie，设定cookie不是办法。仅在IP没有被封情况下可用"""
        url = "http://weixin.sogou.com"
        try:
            for i in xrange(0, 15):  # 生成10个新的cookie
                self.s = requests.Session()
                self.s.headers = self.headers
                query = ''.join(random.choice(string.lowercase) for i in range(random.choice(range(4, 8))))
                self.s.get('http://weixin.sogou.com/')
                self.s.headers['Host'] = 'pb.sogou.com'
                self.s.headers['Referer'] = 'http://weixin.sogou.com/'
                r3 = self.s.get('http://pb.sogou.com/pb.js')
                # print r3.headers, 99999999999999999
                ck = requests.utils.dict_from_cookiejar(self.s.cookies)
                cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()])
                # print ck
                print cookie_string
                # quit()
                self.s.headers['Referer'] = 'http://weixin.sogou.com/'
                self.s.headers['Host'] = 'weixin.sogou.com'
                r = self.s.get('http://weixin.sogou.com/weixin?type=1&query={}&ie=utf8'.format(query))
                # print r.headers
                ck = requests.utils.dict_from_cookiejar(self.s.cookies)
                # print ck
                cookie_string = "; ".join([str(x)+"="+str(y) for x, y in ck.items()]) + '; weixinIndexVisited=1'
                self.ck_mk.append(cookie_string)
                # self.ck_redis(cookie_string)
                print cookie_string
                logging.info('now get ck str is {}'.format(cookie_string))
                rand_sleep(20, 5)
            print self.ck_mk
            logging.info('get 15 cookie str success and cookie list is {}'.format(str(self.ck_mk)))
            return True
        except Exception, e:
            logging.error('try to get cookie from sogou error and msg is {}'.format(str(e)), exc_info=True)


    def rand_ua(self):
        self.s.headers['User-Agent'] = random.choice(self.ua_list)
        print 'switching ua'
        logging.info('switching ua')
        return True

    def rand_ck(self):
        self.s.headers['cookie'] = random.choice(self.cookie_list)
        print 'switching cookie'
        logging.info('switching ck')
        return True

    def rand_ck3(self):
        self.s.headers['cookie'] = random.choice(self.ck_mk)
        print self.s.headers['cookie']
        print 'switching cookie 3'
        logging.info('switching made cookie str')
        return True


    def tmp_ext(self, name, open_id):
        # url2 = 'http://weixin.sogou.com/gzh?openid=' + openid
        try:
            comp = r'\"\S+' + open_id + r'\S+\"'
            print comp
            p = re.compile(comp)
            url2 = 'http://weixin.sogou.com/weixin?'
            self.s.headers['cookie'] = 'weixin.sogou.com'
            data = {
                'type':1,
                'query': name,
                'ie':'utf8',
            }
            r2 = self.url_get(url2, params=data)
            # print r2.text
            print re.search(p, r2.text).group()
            a = re.search(p, r2.text).group()
            ext = a.split('ext=')[1]
            return ext
        except Exception, e:
            logging.error('tmp_ext error msg is {}'.format(str(e)), exc_info=True)

    def tmp_name(self, url):
        try:
        # 直接输入链接，解析出 微信号
        # url2 = 'http://weixin.sogou.com/gzh?openid=' + openid
        # comp = r'\"\S+' + open_id + r'\S+\"'
        # print comp
        # p = re.compile(comp)
            if url.startswith('https://'):
                url.replace('https:', 'http:')
            self.s.headers['Host'] = 'weixin.sogou.com'
            r2 = self.url_get(url)
            # print r2.text
            soup = BeautifulSoup(r2.text, 'html.parser')
            name = soup.find('span', {'class': 'profile_meta_value'}).get_text()
            print name
            return name
        except Exception, e:
            logging.error('tmp_name error error msg is {}'.format(str(e)), exc_info=True)

    def tmp_ext2(self, name):
        # 由微信号得到ext, open_id
        try:
            open_id, ext, weixin = None, None, None
            url = 'http://weixin.sogou.com/weixin?'
            if not url.startswith('http://'):
                url = 'http://' + url
            print self.s.headers
            self.s.headers['Host'] = 'weixin.sogou.com'
            data = {
                'type':1,
                'query': name,
                'ie':'utf8',
            }
            self.s.headers['Referer'] = 'http://weixin.sogou.com/weixin?type=1&query={}&ie=utf8'.format(name)
            r2 = self.url_get(url, params=data)
            print r2.url
            logging.info('tmp url for ext is {}'.format(r2.url))
            soup = BeautifulSoup(r2.text, 'html.parser')
            soup2 = soup.find_all('div', {'class': 'wx-rb bg-blue wx-rb_v1 _item'})
            for i in soup2:
                if i.find('label', {'name': 'em_weixinhao'}).get_text().lower() == name.lower().strip():
                    tmp_lk = i.get('href')
                    tmp_lk = tmp_lk.split('openid=')[1]
                    open_id = tmp_lk.split('&ext=')[0]
                    ext = tmp_lk.split('&ext=')[1]
                    weixin = i.find('div', {'class': 'txt-box'}).h3.get_text()
                    # print open_id, ext, weixin
                    break
            return open_id, ext, weixin
        except Exception, e:
            logging.error('tmp ext2 error get ext openid from wechat id {} error msg is {}'.format(name, str(e)), exc_info=True)


    def url_get(self, url, params={}):
        try:
            self.s.headers['Host'] = url.split('/')[2]
            r = self.s.get(url, params=params)
            self.s.headers['Host'] = 'www.sogou.com'
            self.s.get('http://www.sogou.com/sug/css/m3.min.v.2.css')
        except Exception, e:
            print Exception, str(e)
            logging.error('url get error msg is {}'.format(str(e)), exc_info=True)
            rand_sleep(10)
            r = self.url_get(url, params)
        return r


    def tmp_link(self, ext, openid, page):
        data = {
        'openid': 'oIWsFt86NKeSGd_BQKp1GcDkYpv0',
        'ext': '_vj5mXzN99pxEq14mzKCSlchEFns4L4BnkbE4PXkvcknPRsS-EIBbQR8jt7-WXIL',
        'cb': 'sogou.weixin_gzhcb',
        'page': '1',
        'gzhArtKeyWord': '',
        'tsn': '0',
        # 't': '1456826139004',
        # '_': '1456826138406'
        }
        data['ext'] = ext
        data['openid'] = openid
        data['page'] = page
        url3 = 'http://weixin.sogou.com/gzhjs?'
        self.s.headers['Host'] = url3.split('/')[2]
        # print url3
        r3 = self.url_get(url3, params=data)
        print r3.url

        if r3.url.find('antispider') > 0:
            print 11111111111111111111111111111111111111
            rand_sleep(30, 10)
            print self.s.headers['cookie']
            self.ck_mk.remove(self.s.headers['cookie'])
            # self.cookie_list.remove(self.s.headers['cookie'])
            self.rand_ua()
            self.rand_ck3()
            r3 = self.url_get(url3, params=data)
            print r3.url
        if r3.url is None:
            return None
        # print r3.text
        rtext = r3.text
        # print rtext.find('(')
        rjson = rtext[rtext.find('(')+1:-1*rtext[::-1].find(')')-1]
        # print rjson
        try:
            aaa = json.loads(rjson)
        except Exception, e:
            print Exception, str(e)
            print rjson
            aaa = None
        return aaa


    def real_link(self, tmp_url):
        """微信现在返回的是临时的链接，发现可以在微信端打开，还原为之前的永久链接"""
        try:
            tmp_url += '&ascene=1&uin=MTgzOTMzNDI3MA%3D%3D&devicetype=Windows+7&version=62000050'
            r = self.s.head(tmp_url)
            tmp_url = r.headers['location']
        except Exception as e:
            logging.error('translate tmp_url error error msg is {}'.format(e))
        return tmp_url


    def select(self, url, table):
        # db = sqlite3.connect('wechat.db')
        db = MySQLdb.connect(**self.sql_config)
        sql_sl = """ select url from `news` where url = '{}' and source = '{}' limit 1 """.format(db.escape_string(url), table)
        # print sql_sl
        try:
            cursor = db.cursor()
            cursor.execute(sql_sl)
            data = cursor.fetchall()
            # print url
            db.close()
            # print data
            # print len(data)
            if len(data) > 0:
                # print 22222222222
                logging.info('url in sql')
                return True
            else:
                return False
        except Exception, e:
            logging.error('error msg is {}'.format(str(e)), exc_info=True)
            return False

    def sql_create(self, name):
        # db = sqlite3.connect('wechat.db')
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
            sql_cr = ''' create table If not EXISTS `news`
            (
            source VARCHAR (255),
            url varchar(255) PRIMARY key,
            title varchar(255),
            content varchar(255),
            keyword varchar(255),
            pub_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            add_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
            db.execute(sql_cr)
            db.commit()
            return True
        except Exception, e:
            logging.error('error msg is {}'.format(str(e)), exc_info=True)

    def we_list(self):
        db = MySQLdb.connect(**self.sql_config)
        cursor = db.cursor()
        sql_conf = """select `name` from news_info where `source` = 'WeChat' and `interval` != '0' """
        cursor.execute(sql_conf)
        data = cursor.fetchall()
        url_list = []
        for i in data:
            url_list.append(i[0])
        print url_list
        return url_list


    def new_home(self, name):
        # 由微信号得到 微信的 公众号主页
        try:
            url = 'http://weixin.sogou.com/weixin?'
            if not url.startswith('http://'):
                url = 'http://' + url
            print self.s.headers
            self.s.headers['Host'] = 'weixin.sogou.com'
            data = {
                'type':1,
                'query': name,
                'ie':'utf8',
            }
            self.s.headers['Referer'] = 'http://weixin.sogou.com/weixin?type=1&query={}&ie=utf8'.format(name)
            r2 = self.url_get(url, params=data)
            print r2.url
            logging.info('tmp url for ext is {}'.format(r2.url))
            soup = BeautifulSoup(r2.text, 'html.parser')
            soup2 = soup.find_all('div', {'class': 'wx-rb bg-blue wx-rb_v1 _item'})
            for i in soup2:
                if i.find('label', {'name': 'em_weixinhao'}).get_text().lower() == name.lower().strip():
                    tmp_lk = i.get('href')
                    # tmp_lk = tmp_lk.split('openid=')[1]
                    # open_id = tmp_lk.split('&ext=')[0]
                    # ext = tmp_lk.split('&ext=')[1]
                    # weixin = i.find('div', {'class': 'txt-box'}).h3.get_text()
                    # print open_id, ext, weixin
                    break
            return tmp_lk #, weixin
        except Exception, e:
            logging.error('tmp ext2 error get ext openid from wechat id {} error msg is {}'.format(name, str(e)), exc_info=True)


    def main(self, ii):
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
          # 遍历所有来源 微信id
            print ii
            i_num = 0  # 成功插入数
            i_num2 = 0  # 更新数，新增的文章
            i_total = 0  # 每次拉到的文章总数
            try:
                logging.info('now is wechat id {} s turn'.format(ii))
                self.rand_ua()
                self.rand_ck3()
                open_id, ext, weixin= self.tmp_ext2(ii)
                if open_id is None:
                    logging.error('get wechat id {} s open id error'.format(ii))
                else:
                    # self.sql_create(ii)
                    flag = True
                    page = 1
                    while page <= 10 and flag:
                        # if flag == False:  # 判断是否还需要下一页
                        #     break
                        self.rand_ua()
                        self.rand_ck3()
                        rand_sleep(14, 6)
                        print '-------------------'
                        url3 = 'http://weixin.sogou.com/gzh?openid={}&ext={}'.format(open_id, ext)
                        r4 = self.s.get(url3)
                        rj = self.tmp_link(ext, open_id, page)
                        if len(rj['items']) == 0:
                            break
                        print 'Now page is', page
                        i_total += len(rj['items'])  # 总数
                        logging.info('now sogou search page is {}'.format(page))
                        for i in range(len(rj['items'])):

                            con = rj['items'][i]
                            soup = BeautifulSoup(con, 'html.parser')
                            ss = soup.find('url')
                            sstext = unicode(ss)
                            # print sstext
                            tmp_url = sstext[sstext.find('/'): -9]
                            if tmp_url.startswith('//mp.weixin.qq.com/s?'):
                                tmp_url = 'http:' + tmp_url
                            else:
                                tmp_url = 'http://weixin.sogou.com' + tmp_url
                            tmp_url += '&ascene=1&uin=MTgzOTMzNDI3MA%3D%3D&devicetype=Windows+7&version=62000050' # 这样一次请求
                            self.s.headers.pop('Host', None)
                            self.s.headers.pop('Referer', None)
                            # print self.s.headers
                            rtext = self.s.get(tmp_url)
                            rurl = rtext.url
                            print rurl
                            if rurl.find('spider') > 0:
                                print rurl, '++++++++++++'
                            rtext = rtext.text
                            # print rtext
                            soup2 = BeautifulSoup(rtext, 'html.parser')
                            # print soup2
                            title = soup2.find('title').get_text().encode('utf8')
                            content = soup2.find('div', {'class': 'rich_media_content'})
                            content = unicode(content).encode('utf8')
                            try:
                                pub_time = soup2.find('em', {'id': 'post-date'}).get_text()
                            except:
                                pub_time = ''
                                print self.s.headers['cookie']
                                print soup2
                            rand_sleep(16, 6)
                            l = [ii, rurl, title, content, pub_time]
                            l2 = []
                            for iii in l:
                                l2.append(db.escape_string(iii))
                            sql_in = """ insert into `news` (source, url, title, content, pub_time) values('{}','{}','{}','{}','{}') """\
                                .format(*l2)
                            print ii
                            aaaa = self.select(rurl, ii)
                            print aaaa
                            if aaaa:
                                flag = False
                                break
                            else:
                                i_num2 += 1
                                page += 1
                                print '____________in_______________'
                                try:
                                    cursor.execute(sql_in)
                                    db.commit()
                                    i_num += 1
                                    logging.info('insert mysql success, url is {}'.format(rurl))
                                except Exception, e:
                                    # print sql_in
                                    print Exception, e
                                    logging.error('error and error msg is {}, sql_in is {}'.format(str(e), sql_in), exc_info=True)
                time_now = datetime.datetime.now()
                if i_num > 0:
                    sql_up = """ update news_info SET `latest_num`='{}', `latest_time`='{}', `update_time` = '{}', `latest_total` = '{}', `latest_num2` = '{}' WHERE `name` = '{}'""".format(
                        i_num, time_now, time_now, i_total, i_num2, ii)
                else:
                    sql_up = """ update news_info SET `update_time`='{}', latest_total='{}', latest_num2 = '{}' WHERE `name` = '{}'""".format(
                        time_now, i_total, i_num2, ii)
                cursor.execute(sql_up)
                db.commit()
            except Exception, e:
                logging.error('error and error msg is {}, '.format(str(e)), exc_info=True)
            db.close()
        except Exception, e:
            logging.error('error msg is {}'.format(str(e)), exc_info=True)


    def home_parser(self, html):
        # soup = BeautifulSoup(html, 'html.parser')
        # we_all = soup.find_all('h4', {'class': 'weui_media_title'})
        # print we_all
        # url_list = ['http://mp.weixin.qq.com/' + i.get('hrefs') for i in we_all]
        # return url_list
        p = re.compile("var msgList = '[\S\s]+'")
        rep = re.search(p, html)
        # print rep
        # print rep.group()
        res_dict_str = rep.group().replace('var msgList = ', '').replace("'", "")
        h = HTMLParser.HTMLParser()
        res_list = json.loads(h.unescape(res_dict_str))['list']
        return res_list

    def title_select(self, table, title):
        """url 现在带timestamp了，而且没有规律，现在以一周内同样标题不出现两次"""
        # db = sqlite3.connect('wechat.db')
        week_str = datetime.datetime.now() - datetime.timedelta(days=7)
        db = MySQLdb.connect(**self.sql_config)
        sql_sl = """ select url from `news` where title = '{}' and source = '{}' and add_time > '{}' limit 1
          """.format(MySQLdb.escape_string(title), table, week_str)
        print sql_sl
        try:
            cursor = db.cursor()
            cursor.execute(sql_sl)
            data = cursor.fetchall()
            # print url
            db.close()
            # print data
            # print len(data)
            if len(data) > 0:
                # print 22222222222
                logging.info('title in sql in a week')
                return True
            else:
                return False
        except Exception, e:
            logging.error('error msg is {}'.format(str(e)), exc_info=True)
            return False

    def main2(self, ii):
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
            # 遍历所有来源 微信id
            print ii
            i_num = 0  # 成功插入数
            i_num2 = 0  # 更新数，新增的文章
            i_total = 0  # 每次拉到的文章总数
            try:
                logging.info('now is wechat id {} s turn'.format(ii))
                self.rand_ua()
                self.rand_ck3()
                tmp_home_url = self.new_home(ii)
                print tmp_home_url
                logging.info('get wechat tmp prfile url is {}'.format(tmp_home_url))
                if tmp_home_url is None:
                    logging.error('get wechat tmp home_url {}  error'.format(ii))
                else:
                    self.s.headers.pop('Host', None)
                    self.s.headers.pop('Referer', None)
                    res = self.s.get(tmp_home_url)
                    res_list = self.home_parser(res.text)
                    i_total = len(res_list)
                    for k in res_list:
                        # print k
                        # print type(k)
                        title = k['app_msg_ext_info']['title']
                        content_url = k['app_msg_ext_info']['content_url']
                        print content_url
                        content_url = 'http://mp.weixin.qq.com' + content_url[1:]
                        tmp_url = content_url.replace('amp;', '')
                        tmp_url += '&ascene=1&uin=MTgzOTMzNDI3MA%3D%3D&devicetype=Windows+7&version=62000050'  # 这样一次请求
                        print content_url
                        logging.info('wechat id {} title {} tmp url is {}'.format(ii, title, tmp_url))
                        rtext = self.s.get(tmp_url)
                        rurl = rtext.url
                        print rurl
                        rtext = rtext.text
                        # print rtext
                        soup2 = BeautifulSoup(rtext, 'html.parser')
                        # print soup2
                        # title = soup2.find('title').get_text().encode('utf8')
                        content = soup2.find('div', {'class': 'rich_media_content'})
                        content = unicode(content).encode('utf8')
                        try:
                            pub_time = soup2.find('em', {'id': 'post-date'}).get_text()
                        except:
                            pub_time = ''
                            print self.s.headers['cookie']
                            print soup2
                        rand_sleep(6, 2)
                        l = [ii, rurl, title, content, pub_time]
                        l2 = (MySQLdb.escape_string(iii) for iii in l)
                        sql_in = """ insert into `news` (source, url, title, content, pub_time) values('{}','{}','{}','{}','{}') """ \
                            .format(*l2)
                        print ii
                        aaaa = self.title_select(ii, title)
                        print aaaa
                        if aaaa:
                            flag = False
                        else:
                            i_num2 += 1
                            print '____________in_______________'
                            try:
                                cursor.execute(sql_in)
                                db.commit()
                                i_num += 1
                                logging.info('insert mysql success, url is {}'.format(rurl))
                            except Exception, e:
                                # print sql_in
                                print Exception, e
                                logging.error('error and error msg is {}, sql_in is {}'.format(str(e), sql_in),
                                              exc_info=True)
                time_now = datetime.datetime.now()
                if i_num > 0:
                    sql_up = """ update news_info SET `latest_num`='{}', `latest_time`='{}', `update_time` = '{}', `latest_total` = '{}', `latest_num2` = '{}' WHERE `name` = '{}'""".format(
                        i_num, time_now, time_now, i_total, i_num2, ii)
                else:
                    sql_up = """ update news_info SET `update_time`='{}', latest_total='{}', latest_num2 = '{}' WHERE `name` = '{}'""".format(
                        time_now, i_total, i_num2, ii)
                cursor.execute(sql_up)
                db.commit()
            except Exception, e:
                logging.error('error and error msg is {}, '.format(str(e)), exc_info=True)
                print e
        except Exception, e:
            print e
            logging.error('error and error msg is {}, '.format(str(e)), exc_info=True)

if __name__ == '__main__':
    a = WeChat()
    url_list = a.we_list()
    print url_list
    for ii in url_list:
        a.main2(ii)
    print 'done'
    logging.info('WeChat cycle done')
