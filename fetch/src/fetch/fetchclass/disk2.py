#coding:utf-8
"""
additional file to get diskinfo and resume count in Elasticsearch or more 
"""
import os, sys
import urllib2, json
from datetime import date
from common import root_path
import requests

# ezdbinfo_dir = os.path.join(root_path, 'database', 'ezdbinfo.txt')
#print ezdbinfo_dir

def diskinfo(path): 
    '''磁盘信息'''
    str= os.popen("df -h | grep %s" % path).read()
    result = str.split()
    #print result
    psize = result[1]
    pused = result[2]
    pavail = result[3]
    ppercent = result[4]
    return psize, pused, pavail, ppercent

def redis_info():
    rr = os.popen("redis-cli llen queue").read().strip()
    return rr

def ezdbinfo(module_type):
    '''入搜索库的信息'''
    url = 'http://183.131.144.102:8090/_count?pretty'
    post_dict = {}
    if module_type == 'all':
        url = 'http://183.131.144.102:8090/_count?pretty'
        fname = 'ezdbinfo.txt'
    elif module_type == 'new_all':
        url = 'http://183.131.144.102:8090/supin_resume_v1/doc_v1/_count?'
        fname = 'new_ezdbinfo.txt'
    elif module_type == 'cjol':
        url = 'http://183.131.144.102:8090/supin_resume_v1/doc_v1/_count?'
        post_dict = { "query":{ "match":{"source": "cjol"} } }
        fname = 'cjol_ezdbinfo.txt'
    elif module_type == 'zhilian':
        url = 'http://183.131.144.102:8090/supin_resume_v1/doc_v1/_count?'
        post_dict = { "query":{ "match":{"source": "zhilian"} } }
        fname = 'zhilian_ezdbinfo.txt'
    elif module_type == '51job':
        url = 'http://183.131.144.102:8090/supin_resume_v1/doc_v1/_count?'
        post_dict = { "query":{ "match":{"source": "51job"} } }
        fname = '51job_ezdbinfo.txt'

    ezdbinfo_dir = os.path.join(root_path, 'database', fname)
    r = requests.post(url, data=json.dumps(post_dict))
    #print uget
    # dbcount = json.loads(uget.read())['count']
    dbcount = r.json()['count']
    today = date.today().isoformat()
    todaydata = today + ' ' + str(dbcount) 

    ## if the newest info is not today write today ezdbinfo to ezdbinfo.txt
    with open(ezdbinfo_dir, 'a+') as f:
        fc = f.readline()
        try: preday = fc.split()[0]
        except Exception,e: preday = None
        #print preday, today 
    if not preday == today:
        with open(ezdbinfo_dir, 'r+') as ftmp:
            olddata = ftmp.read()
        with open(ezdbinfo_dir, 'r+') as f2:
            f2.write(todaydata + '\n' + olddata)
            print f2.read()
    return dbcount, ezdbinfo_dir

def exezdbinfo(module_type):
    '''前一天搜索库的信息'''
    ezzz = ezdbinfo(module_type)
    today_num = ezzz[0]
    info_dir = ezzz[1]
    with open(info_dir, 'a+') as f:
        ff = f.readline()
        try: ff = f.readline().split()[1]
        except: ff = 'not recorded'
    return today_num, ff

def ex_msg(module_type):
    aa = exezdbinfo(module_type)
    dbcount = exezdbinfo(module_type)[0]
    exdbcount = exezdbinfo(module_type)[1]
    try:
        incdbcount = int(dbcount) - int(exdbcount)
    except:
        incdbcount = 0
    dbcountmsg = '目前{}搜索库量: '.format(module_type) + str(dbcount) + '  昨天的搜索库量' + str(exdbcount) + ' 增量： ' + str(incdbcount)
    return dbcountmsg, dbcount, exdbcount, incdbcount

def bakinfo():
    '''监测autoMvFile 脚本的运行'''
    s = os.popen('ps aux | grep -v grep | grep "autoMvFile"')
    sr = s.read()
    if sr == '':
        return False
        print('bakcup service offline')
    else:
        return True
        print('backup service online')

def sucinfo(task):
    '''读取successtask_zone.txt文件，反馈成功的数量51与智联search下载的'''
    fname = task + '_successtask_zone.txt'
    fpath = os.path.join(root_path, fname)
    try:
        with open(fpath, 'r') as f:
            sucnum = f.read()
            #print sucnum
        return sucnum
    except:
        sucnum = 0
        #print sucnum
        return sucnum
    
if __name__ == '__main__':
    path = sys.argv[1]
    print diskinfo(path)
