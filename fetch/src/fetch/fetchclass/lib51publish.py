# encoding:utf8

from BaseFetch import BaseFetch
import os,datetime,time,logging
from common import *
from dbctrl import *
import sys
import json
from lib51search import job51search
reload(sys)
sys.setdefaultencoding('utf8')
import logging.config

class job51pub(job51search):
    def __init__(self, ck_str, payload):
        job51search.__init__(self)

        # self.payload = urllib.urlencode(j_payload(self.json_string))
        self.payload = urllib.urlencode(payload)
        self.host=r'ehire.51job.com'
        self.domain='51job.com'
        self.module_name='51publish'

        self.refer=''
        self.headers={
            'Host':self.host,
            'Origin':'http://ehire.51job.com',
            'Referer':'http://ehire.51job.com/Candidate/SearchResume.aspx',
            'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type':'application/x-www-form-urlencoded',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
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
            #begin_num=self.current_num
            self.refer = 'http://ehire.51job.com/Jobs/JobEdit.aspx?Mark=New'
            self.headers['Referer']=self.refer

            self.headers['Host'] = 'ehire.51job.com'
            # self.headers['Origin'] = 'http://rms.cjol.com'
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/43.0'

            url = 'http://ehire.51job.com/Jobs/JobsView.aspx'
            url_p = 'http://ehire.51job.com//Jobs/JobEdit.aspx?Mark=New&AjaxPost=True'

            try:
                #login check and send cookie off email
                html = self.url_post(url, self.payload)
                with open('51pu.html', 'w+') as f:
                    f.write(html)
                logging.info('51 return html is {}'.format(html))
                return html
                # return json.dumps({'status': 'success', 'msg':html})
            except Exception, e:
                logging.error('{} username {} publish jobs fail'.format(self.module_name, self.username), exc_info=True)
        except Exception, e:
            logging.error('{} username {} publish jobs fail'.format(self.module_name, self.username), exc_info=True)

if __name__ == '__main__':
    print 'test...'
    ck_str = 'guid=14634701912151490015; 51job=cenglish%3D0; EhireGuid=6266386fb9664b3a8ce3ac18bdcdc164; ASP.NET_SessionId=hb2rd3phkd5awi0guicq2k4j; HRUSERINFO=CtmID=1772717&DBID=3&MType=02&HRUID=3111730&UserAUTHORITY=1100111010&IsCtmLevle=1&UserName=%e6%b7%b1%e5%9c%b3%e4%ba%8b%e4%b8%9a%e9%83%a83&IsStandard=1&LoginTime=05%2f17%2f2016+15%3a30%3a17&ExpireTime=05%2f17%2f2016+15%3a40%3a17&CtmAuthen=0000011000000001000111010000000011100011&BIsAgreed=true&IsResetPwd=true&CtmLiscense=7&AccessKey=378b20787d6ea44f; AccessKey=b11a01836bfe4a9; EDiaryEditor_RSave=true; LangType=Lang=&Flag=1; Theme=Default'
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
    c = libpublish.Job51(source_json)
    payload = c.j_payload()
    a=job51pub(ck_str, payload)
    a.run_work()