# encoding: utf8

import MySQLdb
import random
import datetime, time
# import common
import json, os
import logging.config, logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from prettytable import PrettyTable
import common

sql_config = common.sql_config
json_config_path = common.json_config_path
log_dir = common.log_dir
#
# init other log
with open(json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(log_dir, 'talentpush.log')
logging.config.dictConfig(log_dict)
logging.debug('hahahahha')

past_month = datetime.datetime.now() - datetime.timedelta(days=31)


def cateall():
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()

    sql = """ select distinct(job_category) from talent """

    cursor.execute(sql)

    data = cursor.fetchall()
    tp_list = []
    for i in data:
        if i[0] is not None:
            tp_list.append(i[0])
    # print tp_list
    logging.info('unique job_category list is {}'.format(str(tp_list)))
    return tp_list

# print ','.join(tp_list)

def catelist(ca, num):  # 从某些类型随机抽出几个
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql = """select id from talent where job_category = '{}' and push_status = 1 order by  clickPushTime limit 25""".format(ca)
    cursor.execute(sql)
    data = cursor.fetchall()
    # print data
    n = len(data)
    if n > 0:
        if n > 5:
            n = random.choice(range(1,5))
        aa = random.sample(data, n)
        print aa, ca
        logging.info('random select these id {} from talent category is {}'.format(str(aa), ca))
        return aa

def up_fuc(lst):
    for i in lst:
        db = MySQLdb.connect(**sql_config)
        cursor = db.cursor()
        logging.info('now to update id {} set clickpushtime '.format(i[0]))
        sql = """update talent set `clickPushTime` = '{}', `isSearch` = '0', `isXrg` = '2' WHERE id = '{}'""".format(datetime.datetime.now(), i[0])
        print sql
        cursor.execute(sql)
        db.commit()
        db.close()
        sec = random.choice(range(60, 30*60))
        logging.info('random sleep time is {}'.format(sec))
        time.sleep(sec)
    return True

def idmerge():  # 返回需要更新的id的列表
    tp_list = cateall()
    upl = []
    for i in tp_list:
        aaa = catelist(i, 2)
        if aaa:
            upl.extend(aaa)
    print upl
    return upl

def denylist():  # 返回所有贤人馆为2的简历id list
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    rand_hour = random.choice(range(1, 8))
    print 'random sleep hour is ', rand_hour
    tt = datetime.datetime.now() - datetime.timedelta(hours=rand_hour)
    sql = """select b.resume_id from talent a join push_talent b where a.isXrg in (2, 3) and
        b.resume_status = 0 and a.id = b.resume_id  and b.invite_time < '{}'""".format(tt)
    cursor.execute(sql)
    data = cursor.fetchall()
    tp_list = [i[0] for i in data]
    logging.info('auto deny list is {}'.format(str(tp_list)))
    return tp_list


def denylist2():
    """返回所有已经修改过的id列表，就是isXrg 为2或者3 的"""
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql = """select id from talent where `isXrg` in (2, 3) """
    cursor.execute(sql)
    data = cursor.fetchall()
    tp_list = [i[0] for i in data]
    logging.info('all modify id_list is {}'.format(str(tp_list)))
    return tp_list


def autodeny(ii):  # 关闭订单，将 push_talent 的 resume_status 设置为 2 拒绝 将
    try:
        db = MySQLdb.connect(**sql_config)
        cursor = db.cursor()
        logging.info('now to update id {} '.format(ii))
        reject_list = [u'联系方式错误', u'该候选人暂不考虑新机会，建议留意其他合适的候选人',
                       u'岗位信息不符合候选人的需求', u'对公司业务不感兴趣', u'暂不考虑该地点的工作',
                       u'您好，该人选已经找到新工作，并且不看机会了，请您留意其他候选人！']
        reject_content = random.choice(reject_list)
        t_now = datetime.datetime.now()
        sql = """update push_talent set resume_status = 2, content = '{}', pass_time = '{}'
            where resume_id = {} """.format(reject_content, t_now, ii)
        cursor.execute(sql)
        sql2 = """update resume_request set `status` = -1 where resume_id = {} """.format(ii)
        cursor.execute(sql2)
        db.commit()
        db.close()
        print 'update resume id {} success'.format(ii)
        return True
    except Exception, e:
        print e
        return False

def run2():
    try:
        ll = idmerge()
        up_fuc(ll)
    except Exception, e:
        logging.error('error msg is {}'.format(e), exc_info=True)

def res():
    """今天自动推送的简历id"""
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql = """select id, job, isXrg, clickPushTime from talent where isXrg in (2, 3)
          and date(clickPushTime) = '{}' """.format(datetime.datetime.today().date())
    cursor.execute(sql)
    data = cursor.fetchall()
    x = PrettyTable([u"简历id", u"job", u"来源", u"推送时间", u"简历链接"])
    x.align[u"简历id"] = 1
    x.sortby = u"来源"
    url_pre = 'http://8082.tuikor.com/web/public/v1.6/index.html#!/resumeDetail/'
    for i in data:
        x.add_row(i + (url_pre + str(i[0]),))
    return x.get_html_string().encode('utf8')

def res2():
    """今天自动拒绝的简历id"""
    ll = denylist2()
    ll2 = [int(i) for i in ll]
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    sql = """select user_id, resume_id, order_id, content, pass_time from
          push_talent where resume_id in {} and resume_status = 2
          and date(pass_time) = '{}' """.format(tuple(ll2), datetime.datetime.today().date())
    cursor.execute(sql)
    data = cursor.fetchall()
    x = PrettyTable([u"用户id", u"简历id", u"订单id", u"拒绝理由", u"拒绝时间"])
    x.align[u"用户id"] = 1
    x.sortby = u"拒绝时间"
    # url_pre = 'http://8082.tuikor.com/web/public/v1.6/index.html#!/resumeDetail/'
    for i in data:
        x.add_row(i) # + (url_pre + str(i[0]),))
    return x.get_html_string().encode('utf8')

def res_email():
    msg_style = '''<html>
    <head>
        <meta charset="utf-8">
    </head>
    <style type="text/css">

    .body{
      font-family: Monaco, Menlo, Consolas, "Courier New", "Lucida Sans Unicode", "Lucida Sans", "Lucida Console",  monospace;
      font-size: 14px;
      line-height: 20px;
    }

    .table{ border-collapse:collapse; border:solid 1px gray; }
    .table td{border:solid 1px gray; padding:6px;}

    .color-ok {color: green;}
    .color-warning {color: coral;}
    .color-error {color: red;}

    .bg-ok {background-color: lavender;}
    .bg-warning {background-color: yellow;}
    .bg-error {background-color: deeppink;}
    </style>

    <body class="body">
    <h2>talent 当天推送简历id列表，来源为2 的是本来就是talent表的数据，
    来源为3 的表示从搜索库过来的， 目前现在测试服测试推送效果，可以了部署到正式服上去<br>
    16:30 推送talent表来源的， 10:35和13:35推送搜索库来源的，搜索库来源的都是当天入库（更新的）</h2>'''
    msg = res()
    msg2 = res2()
    msg = msg_style + msg + "<br><br>今天自动拒绝的简历id列表，拒绝理由随便写的<br><br>" + msg2
    msg += '</body>' + '</html>'
    msg = msg.replace('<table>', '<table class="table">').replace('<th>', "<th class='table'>")
    common.sendEmail(title='talent表自动推送简历列表(测试服)', message=msg)

if __name__ == '__main__':
    if sys.argv[1] == 'deny':
        ll = denylist()
        print 'to deny list is', ll
        for i in ll:
            print 'try to deny  ', i
            if autodeny(i):
                print 'deny resume_id {} success'.format(i)
            else:
                print 'deny resume_id {} fail'.format(i)
    elif sys.argv[1] == 'push':
        run2()
    elif sys.argv[1] == 'email':
        # msg = res()
        res_email()

