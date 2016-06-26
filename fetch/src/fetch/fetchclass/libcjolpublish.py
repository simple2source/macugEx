#-*- coding:UTF-8 -*-
##Todo clean messy previsous codes(useless) cuz dont need task files anymore 

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
from dbctrl import *
from bs4 import BeautifulSoup
import re
from time import gmtime, strftime
import json, random
from redispipe import *
import libaccount
import logging.config
from extract_seg_insert import ExtractSegInsert
# import extract_seg_insert.cjolextract_new
import libcjolsearch


class Cjolpub(libcjolsearch.mainfetch):
    def __init__(self, ck_str, payload=''):
        libcjolsearch.mainfetch.__init__(self)
        self.payload = payload
        self.host=r'rms.cjol.com'        
        self.domain='cjol.com'
        self.module_name='cjolpublish'
        
        self.refer=''
        self.headers={
            'Host':self.host,                    
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
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
            self.load_cookie(self.cookie_fpath)
            self.refer = 'http://newrms.cjol.com/jobpost/jobpost'
            self.headers['Referer']=self.refer
            self.headers['Host'] = 'newrms.cjol.com'
            self.headers['Origin'] = 'http://newrms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
            url = 'http://newrms.cjol.com/JobPost/SaveJobPostInfo?action=Add&jobpostid=-1'
            try:
                #login check and send cookie off email
                # self.login()
                self.payload = urllib.urlencode(self.payload)
                print self.payload
                html = self.url_post(url, self.payload)
                print html
                html_json = json.loads(html)
                if html_json['Succeded']:
                    post_id = json.loads(html_json['OtherData'])['JobPostID']
                    job_url = 'http://www.cjol.com/jobs/job-{}?FromFlag=100'.format(post_id)
                    res = json.dumps({'status': 'success', 'job_url': job_url, 'msg': 'data from cjol is {}'.format(html)})
                else:
                    res = json.dumps({'status': 'fail', 'msg': 'data from cjol is {}'.format(html)})
                with open('cjolp.html', 'w+') as f:
                    f.write(html)
                logging.info('cjol return html is {}'.format(html))
                print res
                return res
            except Exception,e:
                logging.error('{} username {} publish jobs fail'.format(self.module_name, self.username), exc_info=True)
        except Exception,e:
            logging.error('{} username {} publish jobs fail'.format(self.module_name, self.username), exc_info=True)


if __name__ == '__main__':
    print 'test...'
    ck_str = '_isTipsOvered=1; newrms_masterct=newrms08_ct; isFirstLoad=1; ASP.NET_SessionId=iwg3knas4prxswfwcun1izwq; status_id=-1; KwdSearchListOrderBy=UpdateTime%20desc; __utma=97906509.1768109624.1448422117.1462528913.1462531086.975; __utmc=97906509; __utmz=97906509.1456113829.972.119.utmcsr=newrms.cjol.com|utmccn=(referral)|utmcmd=referral|utmcct=/Default; IsLoginFromSMS=0; CjolRmsSsoFormV7=22623543E0771A6280D97EDAA125E9854AC31303F85888AA7C51209C3AB9F3704E941EFBB1445C2FFA62B0538FC97F3293D04A8D139E5C0E526C5A061BECD916B32189AD7412510267CCB2AFB671179D14ADF200E08E80FB60FCDAFE5128BD348FF35A7B540BB62C4486C18F73554ED104061ADF20A0157BC7E70B585596765B22FFD31290887AFE7A10F6F4B92CEB0C1E10FFB497BB529299748F65CAF9EBA2B254E5995A903250B5048838B5D97E7E3128F09874909F25E349C34E74F44BA7C47898CFB06884D66FDFCAD0606CCDC6236FB2ACFC45D5F8870FCC8CDE145B19EB957880760C6A57C2908712D8C32834ECD874D43DF4C2F96186D7C748993FE0C34E0F3476A2D095CE70512CBA414F2D4585CB16AEEB41D3A46A73F2606DF2F3F79390624992A3BD7395330667CAF6410FDEA91A4D02492599C3BEA3761EFC304817A6EAA0D47DDCBD3D7A93464DAE369CEDD19263600566FC0285DC23FDF7CFB797B50EE15A66570A3E88D6B8723FEB75CFDBE6D089D649F56C4CAA7EB9E490D10A085AF38CED99F8D77A192EF0B9AA48150250FC0CA2E925D2BCCF2CE8119ED0A30CAE8CA04C329A8FFD8EB289D403CEAFA2198F385A334F7B1159EBA38CEAF092F510CA50F8BEA00D9A5D8F182C7B9EF64CC82DB463740894FE8EA0594E351C6271322F0892E5677C98FE594C5E85B9ABEA6F616EFE1E6C02DE44B400782518E6D7A0BCCC3C2B41FB61F26A6521179691C34F6458B71983A0B69A581466C268B82C6A47B64049AEA4CF8341831F76417B0E261B2EF1C4AFFBBF3446F67DFAD441644EAF2C0BA799C4E1ED55FD393F51722D6B1A4198CA563C7CB3133EA23AFE1AFDAC8150FF57679994E237C9E1D6FCB60D7C2B3E5318118D3DFFFE43EEBBD8E7C61FC6502DD45BD4EA012B7C98009BDD11DA477DF9E535B239A748B76E0E30B4612EF3003C3C73D32342D847022FAB86283FF4D72C60A41D44695222B3BE73D647BE560913471024003ADE17E50EFBBFF401F85F6BE06F0E03D07CDD8115D45C64220CA3CF873FAA0884B10FA51810E3138BF0FAA18499F7D04D9AEFF75CD08921F72809DBDF5142A1A3110244C27CEB214F2A5EA320E70D9B76A84DE982A522B8B76D605271CBBCE0A6509ED55B1C25C9FEDD9FB55C73C8B5308758AD52BA1235F913163268C6A1D743C63DF469271F3A95ED9B705CFF186D81ECCFDB0119EB0967451A4CE86906FF434D6A32BD96F89C411A29F52B93A492C050ED191E2F4F907E4DDAC6B196308C0C88BC8638DC7D4BC5F94365298CC7ACAAF63E8A7AD27BD50FA51FC80911E5AEA92F057345AD90B263377A9A3808AEFADFB9E8157860C67BE0A1E44DFABF666E919BE58F5022361A09E15D15812A27DDFE8B83C1C42B310E113D445EDDA7B6BF96D13C0A6E012AAF96EE88EA2B2CDEECAFE19F5DA599B73A239EB488BC74121E61A6C4173E426D2EC3798999607705D083A1047666A4B0A40982BC3E21D6B1551BC39C2C6A4CCA976511B4F996F73C3ADBAC4B8AB47DDD47886993260D1A4607732EF5E536A360ADB71282A14779E10A1A0CE9F4F7E6026DFBE6E0C741B2CB1E4C8DC5960D2B6710DE518F4C15762D65BFB2FFC467C8DEF57D9F2627D25EF9285E6773E25498074CF9E741BE7528CA3A421EFE631B7A5A7C49; ServerID=0; CompanyID=317080; CurrentUserGUID=D61DBB9767EE3983328CE7356E40A044; Hm_lvt_36534f4826de8bde820fa4722f1fa7e8=1461050603; Hm_lpvt_36534f4826de8bde820fa4722f1fa7e8=1463468165; mobilenumber=null; isPopup=true'
    source_json = {
        'source': 'cjol',
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
    c = libpublish.Cjol(source_json)
    payload = c.j_payload()
    a=Cjolpub(ck_str, payload)
    a.run_work()
