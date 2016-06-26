#-*- coding:UTF-8 -*-

'''
本文件之中的函数属于作业控制模块，其中的函数暂时没有直接使用，后续开发可以直接忽略进行重新编写
'''

import os,threading,logging,time,random,sys
from fetchclass.BaseFetch import BaseFetch
from fetchclass.libcjol import *
from fetchclass.libjob51 import *
from fetchclass.lib51search import *
from fetchclass.libzhilian import *
from fetchclass.common import task_root,cookie_root
from fetchclass.lib51down import *

def load_task(moudle_name=''):
    '''功能描述：从任务目录下载入各个分级目录的任务文件返回字典'''
    try:
        if moudle_name:
            task_dict={}
            for item in os.listdir(task_root):
                path_one = os.path.join(task_root,item)
                if os.path.isdir(path_one) and moudle_name == item :
                    tmp=[]
                    for sub in os.listdir(path_one):
                        path_two=os.path.join(path_one,sub)
                        if os.path.isfile(path_two) and str(sub).endswith('.txt'):
                            tmp.append(path_two)
                    task_dict[item] = tmp
            return task_dict[moudle_name]
        else:
            return None
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return None
    
def load_cookie(moudle_name=''):
    '''功能描述：从任务目录下载入各个分级目录的cookie文件返回字典'''
    try:
        if moudle_name: 
            cookie_dict={}
            for item in os.listdir(cookie_root):
                path_one = os.path.join(cookie_root,item)
                if os.path.isdir(path_one) and moudle_name == item:
                    tmp=[]
                    for sub in os.listdir(path_one):
                        path_two=os.path.join(path_one,sub)
                        if os.path.isfile(path_two) and sub.endswith('.txt'):
                            tmp.append(path_two)
                    cookie_dict[item] = tmp
            return cookie_dict[moudle_name]
        else:
            return None
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return None

def thread_factory(moudle_name='',para_list=[]):
    '''功能描述：线程工厂根据不同的模块名制作启动不同的抓取工作线程'''
    try:
        for item in para_list:
            print item
        if moudle_name == 'cjol':
            a=cjolfetch(para_list[0],para_list[1])
            a.maxsleeptime=0
            a.run_work()
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False
    
def work_fun():
    '''功能描述：工作函数入口，临时性，采用了线程阻塞机制；后续可以忽略此函数进行重写'''
    try:
        moudles=['cjol']
        for name in moudles:        
            if name == 'cjol':
                tasklist=load_task(name)
                cookielist=load_cookie(name)
                while not cookielist:
                    cookielist=load_cookie(name) 
                thlist=[]
                for subtask in tasklist:
                    cookfpath= random.choice(cookielist)                
                    tmp=''
                    tmp=threading.Thread(target=thread_factory,args = (name,[cookfpath,subtask]))
                    tmp.setDaemon(True)
                    thlist.append(tmp)
                    tmp.start()
                    tmp.join()
        return True
    except Exception,e:
        logging.debug('error msg is %s ' % str(e))
        return False

if __name__ =='__main__':
    moudle_name=''#抓取模块名称
    ck_path=''#cookie路径
    tk_path=''#task任务路径
    id_num=''#简历id下载
    try:
        moudle_name=sys.argv[1]
        ck_path=sys.argv[2]
        tk_path=sys.argv[3]
    except:
        pass
    if moudle_name == 'cjol':
        if ck_path and tk_path:
            work_line=cjolfetch(ck_path,tk_path)   
            work_line.run_work()
    elif moudle_name == '51':
        if ck_path and tk_path:
            work_line=job51fetch(ck_path,tk_path)
            work_line.run_work()
    elif moudle_name == '51search':
        if ck_path and tk_path:
            work_line=job51search(ck_path,tk_path)
            work_line.run_search()
    elif moudle_name == 'zhilian':
        if ck_path and tk_path:
            work_line=zhilianfetch(ck_path,tk_path)
            work_line.run_search()
    elif moudle_name == 'down51':
        if ck_path:
            id_num=sys.argv[3]
            work_line=down51job(ck_path,id_num)
            work_line.run_down()



