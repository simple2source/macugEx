#-*- coding:UTF-8 -*-

import urllib2,urllib,cookielib
import logging,os,shutil
import smtplib,ConfigParser, json
from email.mime.text import MIMEText
import logging.config


root_path=os.path.dirname(os.path.abspath(__file__))
root_path=os.path.dirname(root_path) #根目录
database_path = os.path.join(root_path,'database','fetch.db') #数据库文件路径
db_root = os.path.join(root_path,'db')#简历文件存储路径
conf_dir=os.path.join(root_path,'conf')#配置文件存放目录
cookie_root = os.path.join(root_path,'cookie')#cookie根目录，下有各个数据源的次级目录
task_root = os.path.join(root_path,'task')#任务根目录，下有各个数据源的次级目录
error_root = os.path.join(root_path,'error')#出错信息根目录，下有各个数据源的次级目录
log_dir = os.path.join(root_path,'log')#日志文件目录
buy_database_path = os.path.join(root_path, 'database', 'buy.db')
stat_db_path = os.path.join(root_path, 'database', 'autologin.db')
database_root = os.path.join(root_path, 'database')

basic_confpath=os.path.join(conf_dir,'basic.conf')
json_config_path = os.path.join(conf_dir, 'logging.json')

basic_dirs=[db_root,conf_dir,cookie_root,task_root,error_root]
for item in basic_dirs:
  if not os.path.isdir(item):
    os.makedirs(item)


sql_config_path = os.path.join(conf_dir, 'sql.json')
with open(sql_config_path) as f:
  sql_config = json.load(f)

#根据用户名查找企业名    
job51_account_info={'test0005':'盛德咨询2'}


def url_post(url,postdict={},headers={},timeout=10):
  '''功能描述：通用post方法提交'''
  try:
    if not url.startswith("http://"):
      url = r"http://"+url
    post_str=''  
    cj = cookielib.CookieJar()
    #opener = urllib2.build_opener(urllib2.ProxyHandler({'http': '127.0.0.1:8888'}), urllib2.HTTPCookieProcessor(cj)) #通过代理强求转发post
    # proxy_handler = urllib2.ProxyHandler({'http':'192.168.1.92:8888'})
    # cookie_support = urllib2.HTTPCookieProcessor(cj)
    # opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)
    # urllib2.install_opener(opener)
   # if postdict is string:
   #  post_str = postdict
    if isinstance(postdict,dict):
      post_str = urllib.urlencode(postdict)
    if postdict:
      post_str = postdict
    if post_str:
      if headers:
        req = urllib2.Request(url,post_str,headers)
      else:
        req = urllib2.Request(url,post_str)
    else:
      if headers:
        req = urllib2.Request(url,'',headers)
      else:
        req = urllib2.Request(url)    

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
      html = response.read()   
      return html
    except urllib2.URLError as e:
      pass
    finally:
      if response:
        response.close()
  except Exception,e:
    logging.debug('post request error msg is %s' % str(e))
    return ''


def proxy_url_post(url, ip, postdict={}, headers={}, timeout=10):
  '''功能描述：通用post方法提交'''
  try:
    if not url.startswith("http://"):
      url = r"http://"+url
    post_str = ''
    cj = cookielib.CookieJar()
    #opener = urllib2.build_opener(urllib2.ProxyHandler({'http': '127.0.0.1:8888'}), urllib2.HTTPCookieProcessor(cj)) #通过代理请求转发post
    proxy_handler = urllib2.ProxyHandler({'http': ip})
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)
    urllib2.install_opener(opener)
   # if postdict is string:
   #  post_str = postdict
    if isinstance(postdict,dict):
      post_str = urllib.urlencode(postdict)
    if postdict:
      post_str = postdict
    if post_str:
      if headers:
        req = urllib2.Request(url,post_str,headers)
      else:
        req = urllib2.Request(url,post_str)
    else:
      if headers:
        req = urllib2.Request(url,'',headers)
      else:
        req = urllib2.Request(url)

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
      html = response.read()
      return html
    except urllib2.URLError as e:
      pass
    finally:
      if response:
        response.close()
  except Exception,e:
    logging.debug('post request error msg is %s' % str(e))
    return ''


def url_get(url,getdict={},headers={},timeout=10):
  '''功能描述：通用post方法提交'''
  try:
    if not url.startswith("http://"):
      url = r"http://"+url

    get_str= ''
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

    # 正常跑不走代理的情况
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    #调试走代理的
    # proxy_handler = urllib2.ProxyHandler({'http':'192.168.1.16:8888'})
    # cookie_support = urllib2.HTTPCookieProcessor(cj)
    # opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)

    urllib2.install_opener(opener)
    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
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


def proxy_url_get(url,ip,getdict={},headers={},timeout=15):
  """ 通过代理请求 """
  try:
    if not url.startswith("http://"):
      url = r"http://"+url

    get_str= ''
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

    # 正常跑不走代理的情况
    # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    # 调试走代理的
    proxy_handler = urllib2.ProxyHandler({'http': ip})
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)

    urllib2.install_opener(opener)
    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
      html = response.read()
      return html
    except urllib2.URLError as e:
      pass
    finally:
      if response:
        response.close()
  except Exception,e:
    logging.debug('get proxy request error msg is %s' % str(e))
    return None
  
def move_file(src,dst):
  '''功能描述：安全方式移动文件'''
  try:
    if os.path.isfile(src):
      if os.path.isfile(dst):
        os.remove(dst)
      shutil.copy(src,dst)
      #os.remove(src)
    return True
  except Exception,e:
    logging.debug('error msg is %s' % str(e))
    return False  
  
def clear_dir(dir_path=''):
  '''功能描述：清空特定目录'''
  try:
    if dir_path:
      if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
      os.makedirs(dir_path)
      return True
    else:
      return False
  except Exception,e:
    logging.debug('error msg is %s' % str(e))
    return False
  
def write_file(fpath,file_str=''):
  '''功能描述：安全方式写入文件，自动处理目录以及重名问题'''
  try:
    father_dir=os.path.dirname(fpath)
    if not os.path.exists(father_dir):
      os.makedirs(father_dir)
    f=open(fpath+'.tmp','wb')
    f.write(file_str)
    f.close()
    os.rename(fpath+'.tmp',fpath)
    return True
  except Exception,e:
    logging.debug('error msg is %s' % str(e))
    return False
  

def sendEmail(moudle_name='', title='', message='',msg_type=0, des='T'):
  '''功能描述：通用发信模块，发送简要的email信息,
  新增加一参数，新增P报表'''
  try: 
    if os.path.exists(basic_confpath):
      cf = ConfigParser.ConfigParser()
      cf.read(basic_confpath)
      server_host=cf.get('email','server')
      uname=cf.get('email','username')
      upass=cf.get('email','password')
      tmp_user=cf.get('email','default_users')
      tmp_puser=cf.get('email','product_users')
      if des == 'test':  # 测试用户名邮件
        tmp_user = cf.get('email','test_users')
      default_list = []
      product_list = []
      for m in tmp_user.split(';'):
        if m and default_list.count(m) == 0:
          default_list.append(m)
      users= default_list
      #产品的邮箱地址
      for m in tmp_puser.split(';'):
        if m and product_list.count(m) == 0:
          product_list.append(m)
      pusers = product_list
      operation_users = ['jerry@tuikor.com', 'vinsonli@tuikor.com']
      if msg_type == 1 and not users:
        users=['kelvin@tuikor.com']
      if des == 'P':
        users=pusers + users
      elif des == 'op':
        users = pusers + operation_users + users
    else:
      logging.info('defaulte conf file not exist.') 
      server_host='smtp.163.com'
      uname='hickwu@163.com'
      upass='HickWu608'
      users=['hick@tuikor.com']
      
    if server_host and uname and upass and users:
      msg = MIMEText(message, _subtype='html', _charset='UTF-8')
      #msg['From'] = uname
      msg['Subject'] = title
      msg['From'] = uname
      msg['To'] = ';'.join(users)

      s = smtplib.SMTP()
      #s.set_debuglevel(1)
      s.connect(server_host)
      s.login(uname,upass)
      s.sendmail(uname, users, msg.as_string())
      s.close()
      return True
    else:
      return False
  except Exception,e:
    logging.debug('error msg is %s ' % str(e))
    return False
  

def log_init(name, filename):
  with open(json_config_path) as f:
    ff = f.read()
  logger = logging.getLogger(name)
  log_dict = json.loads(ff)
  log_dict['handlers']['file']['filename'] = os.path.join(log_dir, filename)
  logging.config.dictConfig(log_dict)
  logger.debug('hahahahha')
  return logger
  
if __name__ =='__main__':
  print 'dsdsdsddd'
  
