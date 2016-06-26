# encoding:utf8

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
from dbctrl import *
import sys
import json
from bs4 import BeautifulSoup
from libzhilian import zhilianfetch
import libaccount
import logging.config
reload(sys)
sys.setdefaultencoding('utf8')


class zhilianpub(zhilianfetch):
    def __init__(self, ck_str, payload):
        zhilianfetch.__init__(self)
        # self.payload = urllib.urlencode(j_payload(self.json_string))
        self.payload = payload
        self.host=r'jobads.zhaopin.com'
        self.domain='zhaopin.com'
        self.module_name='zlpublish'
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
        self.headers['Cookie'] = ck_str
        with open(json_config_path) as f:
            ff = f.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(ff)
        log_dict['loggers'][""]['handlers'] = ["file", "stream", "pub", "error"]
        logging.config.dictConfig(log_dict)
        logging.debug('pub hahahahha')

    def run_work(self):
        '''功能描述：执行任务主工作入口函数'''
        try:
            # self.load_task()
            # 不需要检查登陆态

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
                # self.payload['PriorityRule'] = soup.find('input', {'id': 'PriorityRule', 'name': 'PriorityRule'}).get('value') # 扣除点数，应该要多个账号看一下
                self.payload['DepartmentId'] = soup.find('input', {'id': 'DepartmentId', 'name': 'DepartmentId'}).get('value')
                self.payload['CanPubPositionQty'] = soup.find('input', {'id': 'CanPubPositionQty', 'name': 'CanPubPositionQty'}).get('value')
                self.payload['IsCorpUser'] = soup.find('input', {'id': 'IsCorpUser', 'name': 'IsCorpUser'}).get('value')
                self.payload['LoginPointId'] = soup.find('input', {'id': 'LoginPointId', 'name': 'LoginPointId'}).get('value')
                self.payload['CompanyAddress'] = soup.find('input', {'id': 'CompanyAddress', 'name': 'CompanyAddress'}).get('value')
                self.payload['btnAddClick'] = 'saveasnotpub'   #todo 保存不发布，改成 'saveandpub'  是发布
                # self.payload['PositionApplyReply'] = '-1'
            except Exception, e:
                logging.error('{} set get payload error'.format(self.module_name), exc_info=True)

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
                logging.info('zhilian return html is {}'.format(html))
                return html
                # return json.dumps({'status': 'success', 'msg': html})

            except Exception, e:
                logging.error('{} username {} publish jobs fail'.format(self.module_name, self.username), exc_info=True)
                # self.send_mails()
        except Exception, e:
            logging.error('{} username {} publish jobs fail'.format(self.module_name, self.username), exc_info=True)

if __name__ == '__main__':
    print 'test...'
    ck_str = 'recharge=1; pageReferrInSession=; dywez=95841923.1463470759.1.1.dywecsr=(direct)|dyweccn=(direct)|dywecmd=(none)|dywectr=undefined; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1463470759; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1463470760; _jzqa=1.74242765989378350.1463470761.1463470761.1463470761.1; _jzqc=1; _jzqx=1.1463470761.1463470761.1.jzqsr=zhaopin%2Ecom|jzqct=/.-; _jzqckmp=1; pcc=r=1411505711&t=0; JsOrglogin=1986914963; xychkcontr=22794268%2c0; lastchannelurl=http%3A//rd2.zhaopin.com/portal/myrd/regnew.asp%3Fza%3D2; cgmark=2; JsNewlogin=662304987; isNewUser=1; utype=0; RDpUserInfo=; RDsUserInfo=316629614E724264507356664073576A436551645E6D5673497428663D645B7340675F7755680666076142724664577353664873326A396555645D6D2F733C7459664864247337675777576856665A614A724064547352664B735C6A356526645B6D8F1EFB2F1EFE07352026D2358B380A08CC328FEA7A1524F20A229C354873336A3A655564546D5A73377429664E64557333671B7714684A660E611C7219645D73376627735A6A46655364276D35734F7451665E64577344674A775468526657614A724F64227320664E73566A46655A645F6D5073457450664764547348672E772B6859665E614672446404730E664273556A46655F645D6D2D733F7459664364567343675B77556854665D6147724F64257320664E73526A446558645D6D20733E74596643645D7326672B7758685F662E6132724964257327664173556A40655164526D537344745C6642645D7337672B77586827662E614172466451735D664773556A41655064576D25734B7454664164537343675A77556857665D61437244645D73206630735A6A47655364356D28734F74576648642F7323675777576850665F615D724564577356664873326A23655564576D517341745F666; dywea=95841923.3041251860399168500.1463470759.1463470759.1463470759.1; dywec=95841923; dyweb=95841923.18.8.1463472447298; getMessageCookie=1; __utmt=1; __utma=269921210.169431759.1463470761.1463470761.1463472578.2; __utmb=269921210.2.10.1463472578; __utmc=269921210; __utmz=269921210.1463472578.2.2.utmcsr=jobads.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/Position/PositionAdd'
    source_json = {
        'source': '51job',
        'job_detail': {
            'job_name': 'lal34ala2222',  # 职位名称
            'job_type': '硬件测试',  # 职位类别  这个的话51 的选择太多，先不做判断
            'work_type': '全职',  # 工作性质 全职，兼职
            'city': '广州',  # 发布城市
            'district': '海珠区',  # 区
            'work_address': '高大上',  # 上班地址
            'job_num': '15',  # 招聘人数
            'salary': '19320',  # 月薪，输入数字， 判断选择范围
            'work_year': '3',  # 工作年限，输入数字，判断选择范围
            # 可选
            'degree': '博士',  # 学历
            'major': '计算机科学与技术',  # 专业  智联不需要
            # 'publish_day': '2015-12-31',  # 发布日志，只有cjol有
            # 'department': '',  所属公司部门，意义不大
            # 'sex': '男',  # 性别  51job 没有 只有 cjol 有,  智联把区分性别当做歧视
            'welfare': '五险一金 222 111 高温补贴',  # 福利 以空白做分隔符
            'keyword': '前景 高薪',  # 职位关键词，方便搜索
            'email': 'a@a.com',  # 接受系统自动转发的简历
            'job_describe': '大家好，大家好，大家好。',  # 这是职位描述，用户自行添加
        }
    }
    import libpublish
    c = libpublish.Zhilian(source_json)
    payload = c.j_payload()
    a=zhilianpub(ck_str, payload)
    a.run_work()