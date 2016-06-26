#-*- coding:UTF-8 -*-

import urllib2,urllib,cookielib
import os,random
import logging,time
from logging.handlers import TimedRotatingFileHandler

logdir=os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(logdir):
    os.makedirs(logdir)
logpath=os.path.join(logdir,'51job.log')    

def init_log(): 
    '''功能描述：初始化日志参数'''
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d][%(levelname)s]:%(message)s")
    fileHandle = logging.handlers.RotatingFileHandler(logpath, maxBytes=(10*(1<<20)), backupCount=5)
    fileHandle.setFormatter(formatter)
    logger.addHandler(fileHandle)
    logger.addHandler(console)
init_log()


def url_get(url,getdict={},headers={},timeout=10):
    '''功能描述：通用post方法提交'''
    try:
        if not url.startswith("http://"):
            url = r"http://"+url
        get_str=''
        if getdict:
            get_str = urllib.urlencode(getdict)
        if get_str:
            if headers:
                req = urllib2.Request(url+'?'+get_str)
                for item in headers.keys():
                    req.add_header(item,headers[item])
            else:
                req = urllib2.Request(url+'?'+get_str)
        else:
            req = urllib2.Request(url) 
            if headers:        
                for item in headers.keys():
                    req.add_header(item,headers[item])
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        html = None
        response = None
        try:
            response = opener.open(req,timeout=timeout)
            html = response.read()
            return html 
        except urllib2.URLError as e:
            pass
        finally:
            if response:
                response.close() 
    except Exception,e:
        logging.debug('get request error msg is %s' % str(e))
        return ''
def isResume_chk(html):
        '''功能描述：检查返回内容是否为合格简历'''
        need_login_tags=['<td colspan="2" class="loginbar">',
                              '<input type="button" onclick="loginSubmit']
        resume_tags=['<div id="divResume"><style>','简历编号']
        try:
            flag = -1
            if html:
                if html.find('此人简历保密') > -1:
                    flag = 2
                if html.find('屏蔽') > -1:
                    flag = 3
                for item in need_login_tags:
                    if item and html.find(item) > -1:
                        flag = 0
                        break
                for sub in resume_tags:
                    if sub and html.find(sub) > -1:
                        flag =1
                        break 
            else:
                flag = -2            
            return flag
        except Exception,e:
            logging.debug('error msg is %s'% str(e))
            return -1
def rand_51job(ck_path="",begin_num=0,end_num=0,step=100,count=10,half_area=5):
    '''功能描述：根据ID进行抽样，参数依次为：cookie文件路径，起始值，结束值，抽样步长，每步抽样个数,命中率抽样子区间半长度'''
    try:
        headers={
                'Host':r'ehire.51job.com',                    
                'User-Agent': 'Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            }
       
        if os.path.isfile(ck_path):
            f=open(ck_path,'rb')
            tmp_str=f.read()
            f.close()
            headers['Cookie']=tmp_str
        while begin_num < end_num:
            logging.info('begin to exec num area [%d,%d]' % (begin_num,begin_num+step))
            for sub in range(0,count):
                num=random.choice(range(begin_num,begin_num+step))
                logging.info('begin to get %d' % num)
                try_num=0
                while try_num < 3:
                    url=r"http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=%s" % str(num)
                    html=url_get(url,{},headers)    
                    isResume= isResume_chk(html)
                    if isResume == 1:
                        logging.info("success num id is %d "%num)
                        success_sub=0
                        logging.info('begin to exec sub area [%d,%d]'%(num-half_area,num+half_area))
                        for x in range(num-half_area,num+half_area):
                            url=r"http://ehire.51job.com/Candidate/ResumeView.aspx?hidUserID=%s" % str(x)
                            html=url_get(url,{},headers)    
                            isResume= isResume_chk(html)
                            if isResume ==1:
                                success_sub +=1
                            time.sleep(2)
                        rate=int((float(success_sub)/half_area/2)*100)
                        logging.info('success get %d resumes and the rate is %d%%' % (success_sub,rate))
                        break
                    elif isResume ==0:
                        logging.info('cookie power off')
                        break
                    elif isResume < 0:
                        try_num =0
                        time.sleep(1)
                    try_num +=1                    
                time.sleep(2)
            begin_num += step
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False
    
    
if __name__=='__main__':
    '''功能描述：根据ID进行抽样，参数依次为：cookie文件路径，起始值，结束值，抽样步长，每步抽样个数,命中率抽样子区间半长度'''
    rand_51job('51.txt',86000000,87000000,20000,20,5)
  
  
  