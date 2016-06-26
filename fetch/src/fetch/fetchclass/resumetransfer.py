# encoding: utf8

import requests, time, re
from bs4 import BeautifulSoup
import id_down_51, id_down_cjol, id_down_zhilian
import InputSearch, Inputzhilian
# from lxml import etree
import json
import logging, logging.config
import common
import redis
import pickle
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Trans():
    # C端账号的自动登陆， 获取登录态
    def __init__(self, source, username='', password="", captcha=''):
        self.username = username
        self.source = source
        self.password = password
        self.s = requests.Session()
        self.headers = {
            "Accept":  "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            # "Host": "my.51job.com",   # 51
            # "Referer": "http://my.51job.com/my/113253532/My_Pmc.php?726046007",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/53"
                          "7.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        with open(common.json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['loggers'][""]['handlers'] = ["file", "stream", "trans", "error"]
        logging.config.dictConfig(log_dict)
        logging.debug('hahahahha')
        # 验证码，可选
        self.captcha = captcha
        self.cap = '' # 51的验证码，后面存base64格式的
        self.config={
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            #'connection_pool': self.pool
        }
        self.pool = redis.ConnectionPool(**self.config)
        # 用redis 来过期那些 key，（51 登录第一次失败后需要验证码）
        self.r = redis.StrictRedis(connection_pool=self.pool, **self.config)


    def login_51_check(self, html):
        try:
            lines = html.split("\n")
            last_line = lines[-1].strip()
            res_dict = json.loads(last_line)
            print(html)
            # with open("51co.html", "w+") as f:
            #     f.write(resp01.text.encode(resp01.encoding))
            if res_dict['result'] == 1 and res_dict['status'] == 1:  # 登录成功
                logging.info('{} {} login success'.format(self.source, self.username))
                return 1
            elif res_dict['result'] == 0 and res_dict['status'] == -1:  # 验证码错误
                logging.info('{} {} captcha not correct'.format(self.source, self.username))
                return -1
            elif res_dict['result'] == 0 and res_dict['status'] == -2:  # 登录名或密码错误
                logging.info('{} {} login fail, username or password not correct'.format(self.source, self.username))
                return -2
            elif res_dict['result'] == 0 and res_dict['status'] == -3:  # 需要验证码
                logging.info('{} {} login fail, need captcha to continue'.format(self.source, self.username))
                return -3
            else: # 暂时不清楚情况
                logging.info('do not know what happened: {}'.format(html))
                return -4
        except Exception as e:
            logging.error("something wrong with the return data from 51 {}".format(html), exc_info=True)
            return -5

    def login_51(self):
        # 51 的登陆
        self.headers['Host'] = "www.51job.com"
        self.s.headers = self.headers
        try:
            resp0 = self.s.get("http://www.51job.com/")
            self.headers['Host'] = "my.51job.com"
            self.headers["Referer"] = "http://www.51job.com/"
            self.s.headers = self.headers
            login_url = "http://my.51job.com/my/passport_login.php"
            payload = {
                "from_domain": "www.51job.com",
                "passport_loginName": self.username,
                "passport_password": self.password
            }
            # 尝试登陆
            resp01 = self.s.post(login_url, data=payload)
            return self.login_51_check(resp01.text)
        except Exception as e:
            logging.error("login 51 error {}".format(e), exc_info=True)
            return False

    def login_51_getcap(self):
        """得到验证码"""
        try:
            resp1 = self.s.get("http://my.51job.com/my/passport_verify.php?type=3&from_domain=www.51job.com&t={}"
                               .format(int(time.time() * 1000)))
            with open("111.png", 'wb') as f:
                for chunk in resp1:
                    f.write(chunk)
            self.cap = resp1.content.encode('base64').replace('\n', '')
            print(self.cap)
            redis_key = "Custom51_" + self.username
            self.r.set(redis_key, pickle.dumps(self.s))
            self.r.expire(redis_key, 3600) # 设置超时一个小时
        except Exception as e:
            logging.error("get captcha from 51 error ", exc_info=True)
            return None

    def login_51_cap(self):
        """验证码"""
        try:
            # 登录不成功尝试得到验证码
            payload = {
                "from_domain": "www.51job.com",
                "passport_loginName": self.username,
                "passport_password": self.password
            }
            login_url = "http://my.51job.com/my/passport_login.php"

            # cap = raw_input("hello your captcha: ")
            # print cap
            # payload["passport_verify"] = cap.strip()
            payload["passport_verify"] = self.captcha.strip()
            resp = self.s.post(login_url, data=payload)
            print(resp.text)
            return self.login_51_check(resp.text)

        except Exception as e:
            logging.error("login 51 fail {}".format(e), exc_info=True)
            return False

    def login_51_parse(self):
        """解析登陆成功后的简历id，跟姓名，电话号码"""
        try:
            name, email, phone, resume_id = None, None, None, None
            resp2 = self.s.get("http://my.51job.com/my/My_Pmc.php")
            # print(resp2.encoding)
            # print(resp2.text.encode(resp2.encoding))
            # with open("519.html", "w+") as f:
            #     f.write(resp2.text.encode(resp2.encoding))
            time.sleep(1)
            resp3 = self.s.get('http://my.51job.com/cv/CResume/CV_CResumeManage.php')
            soup = BeautifulSoup(resp3.text, 'html.parser')
            resume_all = soup.find_all('tr', {'class': 'resumeName'})
            for i in resume_all:
                if i.find('a', {'class': 'icon18 iconOpen'}) is not None:
                    preview_url = soup.find('a', {'class': 'icon18 iconSee'}).get('href')
                    resp4 = self.s.get(preview_url)
                    resp4.encoding = 'gbk'
                    soup2 = BeautifulSoup(resp4.text, 'html.parser')
                    name = soup2.find('strong').get_text()
                    # print resp4.text
                    name = name.encode("utf8")
                    try:
                        phone = re.search('1\d{10}', resp4.text).group()
                    except:
                        logging.warning("cannot parse phone from page {}".format(self.source), exc_info=True)
                    try:
                        email = re.search("[\w.]+@[\w.]+", resp4.text).group()
                    except:
                        logging.warning("cannot parse phone from page {}".format(self.source), exc_info=True)
                    try:
                        resume_id = [i for i in preview_url.split("&") if "ReSumeID" in i]
                        resume_id = resume_id[0].split("=")[1]
                    except:
                        logging.warning("cannot parse phone from page {}".format(self.source), exc_info=True)
                    logging.info('get {}, {}, {}, {}'.format(resume_id, name, email, phone))
        except Exception as e:
            logging.error("get {} resume_id error and error msg is {}".format(self.source, e), exc_info=True)
        print resume_id, name, email, phone
        return resume_id, name, email, phone


    def login_zl(self):
        name, email, phone, resume_id = None, None, None, None
        try:
            proxies = {
                'http': 'http://10.4.12.196:8888',
                'https': 'http://10.4.12.196:8888',
            }
            self.headers['Host'] = "passport.zhaopin.com"
            self.headers["Referer"] = "http://www.zhaopin.com/"
            self.s.headers = self.headers
            login_url = "https://passport.zhaopin.com/account/login"
            payload = {
                "int_count": "int_count",
                "errUrl": "https://passport.zhaopin.com/account/login",
                "RememberMe": "true",
                "requestFrom": "portal",
                "loginname": self.username,
                "Password": self.password
            }
            resp = self.s.post(login_url, data=payload, proxies=proxies)
            if resp.text.find(u'正在跳转') < 0:
                return None  # 登录不成功直接返回None
            logging.info('zhilian return is {}'.format(resp.text.encode(resp.encoding)))
            print(resp.text.encode(resp.encoding))
            self.headers.pop("Referer")
            self.headers['Host'] = "i.zhaopin.com"
            self.s.headers = self.headers
            resp2 = self.s.get("http://i.zhaopin.com/", proxies=proxies)
            print(resp2.text)
            with open("519zl.html", "w+") as f:
                f.write(resp2.text.encode(resp2.encoding))
            soup = BeautifulSoup(resp2.text, 'html.parser')
            try:
                name = soup.find('p', {'class': 'basName'}).get_text().strip()
            except:
                logging.warning("cannot parse name from page {}".format(self.source), exc_info=True)
            try:
                phone = re.search('1\d{10}', resp2.text).group()
            except:
                logging.warning("cannot parse phone from page {}".format(self.source), exc_info=True)
            try:
                email = re.search("[\w.]+@[\w.]+", resp2.text).group()
            except:
                logging.warning("cannot parse email from page {}".format(self.source), exc_info=True)
            try:
                resume_id = soup.find('div', {'class': 'myTxt'}).get('data-ext_id')
            except:
                logging.warning("cannot parse resume id from page {}".format(self.source), exc_info=True)
            print resume_id, name, phone, email
        except Exception as e:
            logging.error("get {} resume_id error and error msg is {}".format(self.source, e), exc_info=True)
        return resume_id, name, phone, email


    def login_cjol(self):
        """cjol 用户的自动登陆
        cjol 不是用https 登录，但是也通过了js加密用户名跟密码，（函数实在太复杂了，不重新实现。。）
        用PyExecJS 跟 nodejs 来调用加密的js代码  (依赖 pyexecjs 跟 nodejs）
        http://js.cjolimg.com/v7/Jms/auth/HeadLoginArea.js"""
        # 截取了该网址部分的js加密函数
        js_str = """function jsencrypt(e) {
         var t = e.replace(/\\0/g, ""),
          n = stringToHex(des(desKey, t, 1, 0));
         return n
        }

        function des(e, t, n, r, i) {
         var s = "charCodeAt",
          o = "fromCharCode",
          u = new Array(16843776, 0, 65536, 16843780, 16842756, 66564, 4, 65536, 1024, 16843776, 16843780, 1024, 16778244, 16842756, 16777216, 4, 1028, 16778240, 16778240, 66560, 66560, 16842752, 16842752, 16778244, 65540, 16777220, 16777220, 65540, 0, 1028, 66564, 16777216, 65536, 16843780, 4, 16842752, 16843776, 16777216, 16777216, 1024, 16842756, 65536, 66560, 16777220, 1024, 4, 16778244, 66564, 16843780, 65540, 16842752, 16778244, 16777220, 1028, 66564, 16843776, 1028, 16778240, 16778240, 0, 65540, 66560, 0, 16842756),
          a = new Array(-2146402272, -2147450880, 32768, 1081376, 1048576, 32, -2146435040, -2147450848, -2147483616, -2146402272, -2146402304, -134217728, -2147450880, 1048576, 32, -2146435040, 1081344, 1048608, -2147450848, 0, -134217728, 32768, 1081376, -2146435072, 1048608, -2147483616, 0, 1081344, 32800, -2146402304, -2146435072, 32800, 0, 1081376, -2146435040, 1048576, -2147450848, -2146435072, -2146402304, 32768, -2146435072, -2147450880, 32, -2146402272, 1081376, 32, 32768, -134217728, 32800, -2146402304, 1048576, -2147483616, 1048608, -2147450848, -2147483616, 1048608, 1081344, 0, -2147450880, 32800, -134217728, -2146435040, -2146402272, 1081344),
          f = new Array(520, 134349312, 0, 134348808, 134218240, 0, 131592, 134218240, 131080, 134217736, 134217736, 131072, 134349320, 131080, 134348800, 520, 134217728, 8, 134349312, 512, 131584, 134348800, 134348808, 131592, 134218248, 131584, 131072, 134218248, 8, 134349320, 512, 134217728, 134349312, 134217728, 131080, 520, 131072, 134349312, 134218240, 0, 512, 131080, 134349320, 134218240, 134217736, 512, 0, 134348808, 134218248, 131072, 134217728, 134349320, 8, 131592, 131584, 134217736, 134348800, 134218248, 520, 134348800, 131592, 8, 134348808, 131584),
          l = new Array(8396801, 8321, 8321, 128, 8396928, 8388737, 8388609, 8193, 0, 8396800, 8396800, 8396929, 129, 0, 8388736, 8388609, 1, 8192, 8388608, 8396801, 128, 8388608, 8193, 8320, 8388737, 1, 8320, 8388736, 8192, 8396928, 8396929, 129, 8388736, 8388609, 8396800, 8396929, 129, 0, 0, 8396800, 8320, 8388736, 8388737, 1, 8396801, 8321, 8321, 128, 8396929, 129, 1, 8192, 8388609, 8193, 8396928, 8388737, 8193, 8320, 8388608, 8396801, 128, 8388608, 8192, 8396928),
          c = new Array(256, 34078976, 34078720, 1107296512, 524288, 256, 1073741824, 34078720, 1074266368, 524288, 33554688, 1074266368, 1107296512, 1107820544, 524544, 1073741824, 33554432, 1074266112, 1074266112, 0, 1073742080, 1107820800, 1107820800, 33554688, 1107820544, 1073742080, 0, 1107296256, 34078976, 33554432, 1107296256, 524544, 524288, 1107296512, 256, 33554432, 1073741824, 34078720, 1107296512, 1074266368, 33554688, 1073741824, 1107820544, 34078976, 1074266368, 256, 33554432, 1107820544, 1107820800, 524544, 1107296256, 1107820800, 34078720, 0, 1074266112, 1107296256, 524544, 33554688, 1073742080, 524288, 0, 1074266112, 34078976, 1073742080),
          h = new Array(536870928, 541065216, 16384, 541081616, 541065216, 16, 541081616, 4194304, 536887296, 4210704, 4194304, 536870928, 4194320, 536887296, 536870912, 16400, 0, 4194320, 536887312, 16384, 4210688, 536887312, 16, 541065232, 541065232, 0, 4210704, 541081600, 16400, 4210688, 541081600, 536870912, 536887296, 16, 541065232, 4210688, 541081616, 4194304, 16400, 536870928, 4194304, 536887296, 536870912, 16400, 536870928, 541081616, 4210688, 541065216, 4210704, 541081600, 0, 541065232, 16, 16384, 541065216, 4210704, 16384, 4194320, 536887312, 0, 541081600, 536870912, 4194320, 536887312),
          p = new Array(2097152, 69206018, 67110914, 0, 2048, 67110914, 2099202, 69208064, 69208066, 2097152, 0, 67108866, 2, 67108864, 69206018, 2050, 67110912, 2099202, 2097154, 67110912, 67108866, 69206016, 69208064, 2097154, 69206016, 2048, 2050, 69208066, 2099200, 2, 67108864, 2099200, 67108864, 2099200, 2097152, 67110914, 67110914, 69206018, 69206018, 2, 2097154, 67108864, 67110912, 2097152, 69208064, 2050, 2099202, 69208064, 2050, 67108866, 69208066, 69206016, 2099200, 0, 2, 69208066, 0, 2099202, 69206016, 2048, 67108866, 67110912, 2048, 2097154),
          d = new Array(268439616, 4096, 262144, 268701760, 268435456, 268439616, 64, 268435456, 262208, 268697600, 268701760, 266240, 268701696, 266304, 4096, 64, 268697600, 268435520, 268439552, 4160, 266240, 262208, 268697664, 268701696, 4160, 0, 0, 268697664, 268435520, 268439552, 266304, 262144, 266304, 262144, 268701696, 4096, 64, 268697664, 4096, 266304, 268439552, 64, 268435520, 268697600, 268697664, 268435456, 262144, 268439616, 0, 268701760, 262208, 268435520, 268697600, 268439552, 268439616, 0, 268701760, 266240, 266240, 4160, 4160, 262208, 268435456, 268701696),
          v = des_createKeys(e),
          m = 0,
          g, y, b, w, E, S, x, T, N, C, k, L, A, O, M, _ = t.length,
          D = 0,
          P = v.length == 32 ? 3 : 9;
         P == 3 ? N = n ? new Array(0, 32, 2) : new Array(30, -2, -2) : N = n ? new Array(0, 32, 2, 62, 30, -2, 64, 96, 2) : new Array(94, 62, -2, 32, 64, 2, 30, -2, -2), t += "\0\0\0\0\0\0\0\0", result = "", tempresult = "", r == 1 && (C = i[s](m++) << 24 | i[s](m++) << 16 | i[s](m++) << 8 | i[s](m++), L = i[s](m++) << 24 | i[s](m++) << 16 | i[s](m++) << 8 | i[s](m++), m = 0);
         while (m < _) {
          n ? (x = t[s](m++) << 16 | t[s](m++), T = t[s](m++) << 16 | t[s](m++)) : (x = t[s](m++) << 24 | t[s](m++) << 16 | t[s](m++) << 8 | t[s](m++), T = t[s](m++) << 24 | t[s](m++) << 16 | t[s](m++) << 8 | t[s](m++)), r == 1 && (n ? (x ^= C, T ^= L) : (k = C, A = L, C = x, L = T)), b = (x >>> 4 ^ T) & 252645135, T ^= b, x ^= b << 4, b = (x >>> 16 ^ T) & 65535, T ^= b, x ^= b << 16, b = (T >>> 2 ^ x) & 858993459, x ^= b, T ^= b << 2, b = (T >>> 8 ^ x) & 16711935, x ^= b, T ^= b << 8, b = (x >>> 1 ^ T) & 1431655765, T ^= b, x ^= b << 1, x = x << 1 | x >>> 31, T = T << 1 | T >>> 31;
          for (y = 0; y < P; y += 3) {
           O = N[y + 1], M = N[y + 2];
           for (g = N[y]; g != O; g += M) E = T ^ v[g], S = (T >>> 4 | T << 28) ^ v[g + 1], b = x, x = T, T = b ^ (a[E >>> 24 & 63] | l[E >>> 16 & 63] | h[E >>> 8 & 63] | d[E & 63] | u[S >>> 24 & 63] | f[S >>> 16 & 63] | c[S >>> 8 & 63] | p[S & 63]);
           b = x, x = T, T = b
          }
          x = x >>> 1 | x << 31, T = T >>> 1 | T << 31, b = (x >>> 1 ^ T) & 1431655765, T ^= b, x ^= b << 1, b = (T >>> 8 ^ x) & 16711935, x ^= b, T ^= b << 8, b = (T >>> 2 ^ x) & 858993459, x ^= b, T ^= b << 2, b = (x >>> 16 ^ T) & 65535, T ^= b, x ^= b << 16, b = (x >>> 4 ^ T) & 252645135, T ^= b, x ^= b << 4, r == 1 && (n ? (C = x, L = T) : (x ^= k, T ^= A)), n ? tempresult += String[o](x >>> 24, x >>> 16 & 255, x >>> 8 & 255, x & 255, T >>> 24, T >>> 16 & 255, T >>> 8 & 255, T & 255) : tempresult += String[o](x >>> 16 & 65535, x & 65535, T >>> 16 & 65535, T & 65535), n ? D += 16 : D += 8, D == 512 && (result += tempresult, tempresult = "", D = 0)
         }
         return result + tempresult
        }

        function des_createKeys(e) {
         var t = "charCodeAt";
         pc2bytes0 = new Array(0, 4, 536870912, 536870916, 65536, 65540, 536936448, 536936452, 512, 516, 536871424, 536871428, 66048, 66052, 536936960, 536936964), pc2bytes1 = new Array(0, 1, 1048576, 1048577, 67108864, 67108865, 68157440, 68157441, 256, 257, 1048832, 1048833, 67109120, 67109121, 68157696, 68157697), pc2bytes2 = new Array(0, 8, 2048, 2056, 16777216, 16777224, 16779264, 16779272, 0, 8, 2048, 2056, 16777216, 16777224, 16779264, 16779272), pc2bytes3 = new Array(0, 2097152, 134217728, 136314880, 8192, 2105344, 134225920, 136323072, 131072, 2228224, 134348800, 136445952, 139264, 2236416, 134356992, 136454144), pc2bytes4 = new Array(0, 262144, 16, 262160, 0, 262144, 16, 262160, 4096, 266240, 4112, 266256, 4096, 266240, 4112, 266256), pc2bytes5 = new Array(0, 1024, 32, 1056, 0, 1024, 32, 1056, 33554432, 33555456, 33554464, 33555488, 33554432, 33555456, 33554464, 33555488), pc2bytes6 = new Array(0, 268435456, 524288, 268959744, 2, 268435458, 524290, 268959746, 0, 268435456, 524288, 268959744, 2, 268435458, 524290, 268959746), pc2bytes7 = new Array(0, 65536, 2048, 67584, 536870912, 536936448, 536872960, 536938496, 131072, 196608, 133120, 198656, 537001984, 537067520, 537004032, 537069568), pc2bytes8 = new Array(0, 262144, 0, 262144, 2, 262146, 2, 262146, 33554432, 33816576, 33554432, 33816576, 33554434, 33816578, 33554434, 33816578), pc2bytes9 = new Array(0, 268435456, 8, 268435464, 0, 268435456, 8, 268435464, 1024, 268436480, 1032, 268436488, 1024, 268436480, 1032, 268436488), pc2bytes10 = new Array(0, 32, 0, 32, 1048576, 1048608, 1048576, 1048608, 8192, 8224, 8192, 8224, 1056768, 1056800, 1056768, 1056800), pc2bytes11 = new Array(0, 16777216, 512, 16777728, 2097152, 18874368, 2097664, 18874880, 67108864, 83886080, 67109376, 83886592, 69206016, 85983232, 69206528, 85983744), pc2bytes12 = new Array(0, 4096, 134217728, 134221824, 524288, 528384, 134742016, 134746112, 16, 4112, 134217744, 134221840, 524304, 528400, 134742032, 134746128), pc2bytes13 = new Array(0, 4, 256, 260, 0, 4, 256, 260, 1, 5, 257, 261, 1, 5, 257, 261);
         var n = e.length >= 24 ? 3 : 1,
          r = new Array(32 * n),
          s = new Array(0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0),
          o, u, a = 0,
          f = 0,
          l;
         for (var c = 0; c < n; c++) {
          left = e[t](a++) << 24 | e[t](a++) << 16 | e[t](a++) << 8 | e[t](a++), right = e[t](a++) << 24 | e[t](a++) << 16 | e[t](a++) << 8 | e[t](a++), l = (left >>> 4 ^ right) & 252645135, right ^= l, left ^= l << 4, l = (right >>> -16 ^ left) & 65535, left ^= l, right ^= l << -16, l = (left >>> 2 ^ right) & 858993459, right ^= l, left ^= l << 2, l = (right >>> -16 ^ left) & 65535, left ^= l, right ^= l << -16, l = (left >>> 1 ^ right) & 1431655765, right ^= l, left ^= l << 1, l = (right >>> 8 ^ left) & 16711935, left ^= l, right ^= l << 8, l = (left >>> 1 ^ right) & 1431655765, right ^= l, left ^= l << 1, l = left << 8 | right >>> 20 & 240, left = right << 24 | right << 8 & 16711680 | right >>> 8 & 65280 | right >>> 24 & 240, right = l;
          for (i = 0; i < s.length; i++) s[i] ? (left = left << 2 | left >>> 26, right = right << 2 | right >>> 26) : (left = left << 1 | left >>> 27, right = right << 1 | right >>> 27), left &= -15, right &= -15, o = pc2bytes0[left >>> 28] | pc2bytes1[left >>> 24 & 15] | pc2bytes2[left >>> 20 & 15] | pc2bytes3[left >>> 16 & 15] | pc2bytes4[left >>> 12 & 15] | pc2bytes5[left >>> 8 & 15] | pc2bytes6[left >>> 4 & 15], u = pc2bytes7[right >>> 28] | pc2bytes8[right >>> 24 & 15] | pc2bytes9[right >>> 20 & 15] | pc2bytes10[right >>> 16 & 15] | pc2bytes11[right >>> 12 & 15] | pc2bytes12[right >>> 8 & 15] | pc2bytes13[right >>> 4 & 15], l = (u >>> 16 ^ o) & 65535, r[f++] = o ^ l, r[f++] = u ^ l << 16
         }
         return r
        }

        function stringToHex(e) {
         var t = "charCodeAt",
          n = "",
          r = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F");
         for (var i = 0; i < e.length; i++) n += r[e[t](i) >> 4] + r[e[t](i) & 15];
         return n
        }
        var desKey = "!@#$%26)(*&^cjol<16>:|}{=-/*-+.CJOL@*&^%*()*<299>";"""
        name, email, phone, resume_id = None, None, None, None
        try:
            import execjs
            ctx = execjs.compile(js_str)
            username = ctx.call("jsencrypt", self.username)
            password = ctx.call("jsencrypt", self.password)
            self.headers['Host'] = "www.cjol.com"
            self.headers["Referer"] = "http://www.cjol.com/"
            self.s.headers = self.headers
            payload = {
                "jsoncallback": "jQuery17206813509915044135_1463658082745",
                "userName": username,
                "password": password,
                "actionType": "jsonp",
                "remember": "checked",
                "_": time.time()
            }
            login_url = "http://www.cjol.com/jobseekers/Login.aspx"
            resp = self.s.get(login_url, data=payload)
            print(resp.text)
            logging.info('cjol return {}'.format(resp.text))
            if resp.text.find(u'"Message":"登录成功!"') < 0:
                return None  # 登录失败直接返回None
            # 得到简历预览的页面
            # resume_preview = "http://www.cjol.com/jobseekers/Resume/ResumePreview.aspx?Language=CN"
            # bb = self.s.get(resume_preview)
            # # print(bb.text)
            # soup = BeautifulSoup(bb.text, 'html.parser')
            # resume_id_tag = soup.find("td", {"class": 'resume_info_up'})
            # resume_id_tag.span.extract()
            # print(resume_id_tag.get_text())
            # 从个人主页得到简要信息跟简历id，用简历id 调用 id_down 来抓取简历入库什么的。
            home_url = "http://www.cjol.com/jobseekers/Default.aspx"
            resp2 = self.s.get(home_url)
            soup = BeautifulSoup(resp2.text, 'html.parser')
            try:
                name = soup.find("div", {"id": "ctl00_ContentPlaceHolder1_div_mycjol_name"}).get_text().strip()
            except Exception as e:
                logging.warning("cannot parse name from page {}".format(self.source), exc_info=True)
            try:
                email = soup.find("span", {"id": "ctl00_ContentPlaceHolder1_span_email"}).get_text().strip()
            except Exception as e:
                logging.warning("cannot parse email from page {}".format(self.source), exc_info=True)
            try:
                phone = soup.find("span", {'id': 'ctl00_ContentPlaceHolder1_span_contact'}).get_text().strip()
            except Exception as e:
                logging.warning("cannot parse phone from page {}".format(self.source), exc_info=True)
            try:
                resume_id = soup.find('p', {'id': 'ctl00_ContentPlaceHolder1_p_jobSeekerID'}).get_text().strip()[4:]
            except Exception as e:
                logging.warning("cannot parse resume_id from page {}".format(self.source), exc_info=True)
            print name, email, phone, resume_id
        except Exception as e:
            logging.error("get {} resume_id error and error msg is {}".format(self.source, e), exc_info=True)
        return name, email, phone, resume_id

    def main(self):
        # 用登陆态，返回的简历id 调用之前的 id_down（为了简单点，调用解析简历界面的不能解析简历预览页面）
        try:
            if len(self.username) == 0 or len(self.password) == 0:
                # 保证用户输入长度
                message = json.dumps({"status": "error", "msg": "username or password must not be empty"})
            else:
                message = dict()
                flag_msg = ''' 正常入库:1 正常更新:-1 已在库中搜索失败:-4
                没有工作经验和教育经历:0 解析有问题:-2 来源有问题:-3 操作有问题:-5, false 表示程序异常,
                简历不存在，或者已经入库，不需要更新:-10, 简历id链接不在redis中:-11'''
                if self.source == '51job':
                    # 没有输入验证码的情况，先尝试无验证码情况
                    if len(self.captcha) == 0:
                        no_cap = self.login_51()
                        if no_cap == -3:  # 没有验证码登录失败，返回验证码的base64 字符串
                            self.login_51_getcap()
                            message['status'] = 'error'
                            message['msg'] = "need captcha to continue"
                            message['captcha'] = self.cap
                        elif no_cap == -2: # 用户名密码错误
                            message['status'] = 'error'
                            message['msg'] = "{} username or password not correct".format(self.username)
                        elif no_cap == -5: # 程序出错
                            message['status'] = 'error'
                            message['msg'] = "{} program error".format(self.username)
                        elif no_cap == -4:  # 不明原因错误
                            message['status'] = 'error'
                            message['msg'] = "{} unknown error".format(self.username)
                        elif no_cap == 1:  # 登录成功
                            resume_id, name, email, phone = self.login_51_parse()
                            if resume_id is not None:
                                message["status"] = "ok"
                                message["resume_id"] = resume_id if resume_id else ''
                                message["email"] = email if email else ''
                                message["name"] = name if name else ''
                                message["phone"] = phone if phone else ''
                                try:
                                    # 先搜索一个那个id， 不然不能id down
                                    b = InputSearch.TransportSearch()
                                    b.run_crawl_first(sid=resume_id)
                                    time.sleep(1.5)
                                    a = id_down_51.IdDown51(resume_id)
                                    flag = a.get_id()
                                    message["id_down"] = "code {}, explain {}".format(flag, flag_msg)
                                except Exception as e:
                                    logging.error("get {} resume_id error".format(self.source), exc_info=True)
                                    message["id_down"] = "error, {}".format(e)
                        else:
                            message['status'] = 'error'
                            message['msg'] = "{} what?".format(self.username)
                    elif len(self.captcha) == 4:
                        redis_key = "Custom51_" + self.username
                        if self.r.exists(redis_key):
                            self.s = pickle.loads(self.r.get(redis_key))
                            yes_cap = self.login_51_cap()
                            if yes_cap == 1:
                                resume_id, name, email, phone = self.login_51_parse()
                                if resume_id is not None:
                                    message["status"] = "ok"
                                    message["resume_id"] = resume_id if resume_id else ''
                                    message["email"] = email if email else ''
                                    message["name"] = name if name else ''
                                    message["phone"] = phone if phone else ''
                                    try:
                                        # 先搜索一个那个id， 不然不能id down
                                        b = InputSearch.TransportSearch()
                                        b.run_crawl_first(sid=resume_id)
                                        time.sleep(1.5)
                                        a = id_down_51.IdDown51(resume_id)
                                        flag = a.get_id()
                                        message["id_down"] = "code {}, explain {}".format(flag, flag_msg)
                                    except Exception as e:
                                        logging.error("get {} resume_id error".format(self.source), exc_info=True)
                                        message["id_down"] = "error, {}".format(e)
                                else:
                                    message['status'] = 'error'
                                    message["msg"] = 'cannot find {} any public resume'.format(self.username)
                            elif yes_cap == -1:  # 验证码错误
                                message['status'] = 'error'
                                message['msg'] = "{} captcha not correct".format(self.username)
                            elif yes_cap == -2:  # 用户名密码错误
                                message['status'] = 'error'
                                message['msg'] = "{} username or password not correct".format(self.username)
                            elif yes_cap == -5:  # 程序出错
                                message['status'] = 'error'
                                message['msg'] = "{} program error".format(self.username)
                            elif yes_cap == -4:  # 不明原因错误
                                message['status'] = 'error'
                                message['msg'] = "{} unknown error".format(self.username)
                            else:
                                message['status'] = 'error'
                                message['msg'] = "{} what?".format(self.username)
                        else:
                            message['status'] = 'this email was not recognized login in 1 hour no captcha before'

                    else:
                        message['status'] = "error"
                        message["msg"] = "length captcha is not right"

                elif self.source == 'zhilian':
                    aaa = self.login_zl()
                    if aaa is None:
                        message['status'] = 'error'
                        message['msg'] = 'login fail username or password not correct'
                    else:
                        resume_id, name, phone, email = aaa
                        if resume_id is not None:
                            message["status"] = "ok"
                            message["resume_id"] = resume_id if resume_id else ''
                            message["email"] = email if email else ''
                            message["name"] = name if name else ''
                            message["phone"] = phone if phone else ''
                            try:
                                b = Inputzhilian.TransportZhlian()
                                b.crawl_zhilian(sid=resume_id)
                                time.sleep(1.5)
                                a = id_down_zhilian.IdDownzhilian(resume_id)
                                flag = a.get_id()
                                message["id_down"] = "code {}, explain {}".format(flag, flag_msg)
                            except Exception as e:
                                logging.error("get {} resume_id error".format(self.source), exc_info=True)
                                message["id_down"] = "error, {}".format(e)
                        else:
                            message['status'] = 'error'
                            message["msg"] = 'cannot find {} any public resume'.format(self.username)
                elif self.source == 'cjol':
                    bbb = self.login_cjol()
                    if bbb is None:
                        message['status'] = 'error'
                        message['msg'] = 'login fail username or password not correct'
                    else:
                        name, email, phone, resume_id = bbb
                        if resume_id is not None:
                            message["status"] = "ok"
                            message["resume_id"] = resume_id if resume_id else ''
                            message["email"] = email if email else ''
                            message["name"] = name if name else ''
                            message["phone"] = phone if phone else ''
                            try:
                                a = id_down_cjol.IdDowncjol(resume_id)
                                time.sleep(1.5)
                                flag = a.get_id()
                                message["id_down"] = "code {}, explain {}".format(flag, flag_msg)
                            except Exception as e:
                                logging.error("get {} resume_id error".format(self.source), exc_info=True)
                                message["id_down"] = "error, {}".format(e)
                        else:
                            message['status'] = 'error'
                            message["msg"] = 'cannot find {} any public resume'.format(self.username)
                else:
                    message = {"status": "error", "msg": "not supported source"}
        except Exception as e:
            logging.error("some thing wrong {}, msg is {}".format(self.source, e), exc_info=True)
            message = {"status": "error", "msg": str(e)}
        print message
        return message


if __name__ == '__main__':
    username = 'hickwu1@163.com'
    password = 'HickWu608'
    cc = 'ba9a'
    app = Trans('51job', username, password)
    app.main()


