# coding=utf-8
"""监控stats 表，当单函数 运行超时连续5次时间 大于 1s，或者"""
import threading
import MySQLdb
import datetime
import time
import common
import logging, logging.config
from prettytable import PrettyTable
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# logger = logging.getLogger('')
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)
logger = common.log_init(__name__, 'statmo.log')

# 初始化一个key 用来存储一个 fun_action，带时间，带次数，
# 检查时间超过半个小时，删除key，把次数，添加到邮件里面 (只对100 的有用）
func_dict = {}

def get_con():
    con = MySQLdb.connect(**common.sql_config)
    return con

def calculate_time():
    now = time.mktime(datetime.datetime.now().timetuple())-60*2
    print now
    result = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
    print result
    res2 = datetime.datetime.now() - datetime.timedelta(minutes=120) # 2 个小时
    return res2


def get_data(ext):
    select_time = calculate_time()
    logging.info("select time:" + str(select_time))
    sql = """select count(id) from stats where msgtype = 'fun_action' and stat_time > '{}'
      and ext1 = '{}'""".format(select_time, ext)
    conn = get_con()
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_ext():
    """找出当天出现的ext"""
    today = datetime.datetime.today().date()
    sql = """select distinct(ext1) from stats where msgtype = 'fun_action' and stat_time > '{}'""".format(today)
    # print sql
    logging.info("select ext1")
    con = get_con()
    cursor = con.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    con.close()
    return results

def get_time():
    """找出响应时间 2分钟内"""
    select_time = calculate_time()
    logging.info("select time:" + str(select_time))
    sql = """select ext2 from stats where msgtype = 'fun_action' and stat_time > '{}'
      and ext1 = '{}'""".format(select_time)
    conn = get_con()
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get1hour(ext, tt):
    """找出当前time 一小时的总数"""
    time1 = tt - datetime.timedelta(hours=1)
    sql1 = """select count(id) from stats where ext1 = '{}' and msgtype = 'fun_action' and
      stat_time > '{}' and stat_time < '{}'""".format(ext, time1, tt)
    # print sql1
    con = get_con()
    cursor = con.cursor()
    cursor.execute(sql1)
    data = cursor.fetchall()
    cursor.close()
    con.close()
    res = data[0][0]
    return res

def abnormal(ext):
    now = datetime.datetime.now()
    now1 = datetime.datetime.now() - datetime.timedelta(days=1)
    now2 = datetime.datetime.now() - datetime.timedelta(days=2)
    time0 = time.time()
    c0 = get1hour(ext, now)
    time1 = time.time() - time0
    c1 = get1hour(ext, now1)
    time2 = time.time() - time0 - time1
    c2 = get1hour(ext, now2)
    time3 = time.time() - time0 - time1 - time2
    # print time1
    # print time2
    # print time3
    logging.info('counting use time 0, {}, 1, {}, 2, {}'.format(time1, time2, time3))
    c3 = (c1 + c2)/2
    # print ext, c0, c1, c2, 'c0, c1, c2'
    if (c0 - c3) > 2 * c3:  # 增长率大于 2 倍，应该属于异常
        return True
    else:
        return False


def task():
    while True:
        try:
            logging.info("monitor running")
            exts = get_ext()
            content = ''
            for i in exts:
                ext = i[0]
                if abnormal(ext):
                    logging.info("increase rate is greater than 2,so send mail")
                    content += str(ext) + str(datetime.datetime.now()) + 'increase rate is greater than 2' +'\n'
            if len(content) > 0:
                # print content
                logging.info(content)
                # common.sendEmail(title='fun_action warning', message=content)
            time.sleep(5*60)
        except Exception as e:
            logging.error('monitor err msg is {}'.format(e), exc_info=True)
            print 'asdfkjasljkflasjdf'
            time.sleep(60*60)


def task2():
    while True:
        try:
            logging.info("monitor running")
            exts = get_ext()
            for i in exts:
                ext = i[0]
                results = get_data(ext)
                if results is not None and len(results) > 5:
                    content = "recharge error："
                    logging.info("a lot of error,so send mail")
                    for r in results:
                        content += r[1]+'\n'
                    common.sendEmail(content)
            time.sleep(2*60)
        except Exception as e:
            logging.error('monitor err msg is {}'.format(e), exc_info=True)


def abnormal2(tt):
    time1 = tt - datetime.timedelta(hours=1)
    sql = """select ext1, count(id) from stats where msgtype = 'fun_action' and
      stat_time > '{}' and stat_time < '{}' group by ext1""".format(time1, tt)
    con = get_con()
    cursor = con.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    con.close()
    return data


def get1hour2(ext, tt):
    """找出当前time 一小时的总数"""
    time1 = tt - datetime.timedelta(hours=1)
    sql1 = """select count(id) from stats where ext1 = '{}' and msgtype = 'fun_action' and
      stat_time > '{}' and stat_time < '{}'""".format(ext, time1, tt)
    # print sql1
    con = get_con()
    cursor = con.cursor()
    cursor.execute(sql1)
    data = cursor.fetchall()
    cursor.close()
    con.close()
    res = data[0][0]
    return res


def runing():
    now = datetime.datetime.now()
    now1 = datetime.datetime.now() - datetime.timedelta(days=1)
    now2 = datetime.datetime.now() - datetime.timedelta(days=2)
    time0 = time.time()
    c0 = abnormal2(now)
    time1 = time.time() - time0
    c1 = abnormal2(now1)
    time2 = time.time() - time0 - time1
    c2 = abnormal2(now2)
    time3 = time.time() - time0 - time1 - time2
    logging.info('counting use time 0, {}, 1, {}, 2, {}'.format(time1, time2, time3))
    ll = [i[0] for i in c0]
    ld = dict()
    for i in ll:
        ld[i] = dict()
    for i in c0:
        ld[i[0]][0] = i[1]
    for i in c1:
        if i[0] in ld:
            ld[i[0]][1] = i[1]
    for i in c2:
        if i[0] in ld:
            ld[i[0]][2] = i[1]
    # print ld
    return ld


def compare(ld, multi):
    lll = []
    for i in ld:
        day0 = int(ld[i].get(0, 0))
        day1 = int(ld[i].get(1, 0))
        day2 = int(ld[i].get(2, 0))
        if day0 > 120:
            if (day1 + day2) / 2 * multi < day0:
                lll.append(i)
    return lll




def momo(multi, sl):
    """ 倍数，睡眠时间， 100倍的检测睡眠 3分钟，2倍的睡眠一小时 """
    while True:
        try:
            logging.info("monitor {} multi sleep {} running".format(multi, sl))
            ld = runing()
            lll = compare(ld, multi)
            content = ''
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if len(lll) > 0:
                x = PrettyTable(["fun_name", "今天", "昨天", '前天', "平均值", "次数"])
                x.align["fun_name"] = "l"
                x.border = True
                content += now + u'\n <span style="color:red"> {} </span> 倍于昨天与前天的平均值 \n'.format(multi)
                for i in lll:
                    # content += '  {} this hour today num is {}, yesterday is {}, the day before yesterday is {}'\
                    #     .format(i, ld[i].get(0), ld[i].get(1, 0), ld[i].get(2, 0))\
                    #            + '\n'
                    if multi >= 100:  # 大于100 的才采取这策略
                        if i not in func_dict:
                            x.add_row([i, ld[i].get(0), ld[i].get(1, 0), ld[i].get(2, 0), (int(ld[i].get(1, 0)) +
                                                                                           int(ld[i].get(2, 0))) / 2, 1])
                            func_dict[i] = {}
                            func_dict[i]['time'] = datetime.datetime.now()  # 更新时间
                            func_dict[i]['num'] = 1
                            logger.info('add key in func_dict')
                        else:
                            now = datetime.datetime.now()
                            if datetime.timedelta(hours=1) >= now - func_dict[i]['time'] > datetime.timedelta(hours=0.5):  # 把key 删了，邮件发出来
                                x.add_row([i, ld[i].get(0), ld[i].get(1, 0), ld[i].get(2, 0), (int(ld[i].get(1, 0)) +
                                                               int(ld[i].get(2, 0))) / 2, func_dict[i]['num'] + 1])
                                func_dict.pop(i)
                                logger.info('send email and remove key')
                            elif now - func_dict[i]['time'] > datetime.timedelta(hours=1): # 这个不发邮件，直接移除
                                func_dict.pop(i)
                                logger.info('remove key because it appear before 1 hour')
                            else: # 更新时间， 更新数字，这个就不发邮件了
                                # func_dict[i]['time'] = datetime.datetime.now()  # 更新时间
                                func_dict[i]['num'] += 1
                                logger.info('add num')
                    else:
                        x.add_row([i, ld[i].get(0), ld[i].get(1, 0), ld[i].get(2, 0), (int(ld[i].get(1, 0)) +
                                                                                   int(ld[i].get(2, 0)))/2, 1])
                # print content
                print content.encode('utf8')
                print x.get_string().encode('utf8')
                # logging.info('content is ' + content)
                if x.get_html_string().count('</tr>') >= 2:  # 有才发出邮件出来
                    html = x.get_html_string(sortby=u'今天')
                    msg = html_cr(content.encode('utf8'), html)
                    msg += u"""<br>两个进程<br> 3分钟检测一次，超过前天跟昨天同一小时平均值100倍而且大于120，就会发告警邮件。<br>
                           一小时检测一次，超过前天跟昨天一小时平均值的2倍，就会发告警邮件， <br>
                           次数是半小时内出现的次数（只针对100倍的检测），半小时内出现计数，半小时后再出现将次数发出来"""
                    common.sendEmail(title='fun_action warning', message=msg, des='test')
                    logger.info('sending email')
                else:
                    logger.info('donot send email')
            logging.info('multi {} sleep {} min'.format(multi, sl))
            time.sleep(sl*60)
        except Exception as e:
            logging.error('monitor err msg is {}'.format(e), exc_info=True)
            print 'asdfkjasljkflasjdf'
            time.sleep(60*60)

def html_cr(header, content):
    msg_style = """<style type="text/css">
    .body{
    font-family: Monaco, Menlo, Consolas, "Courier New", "Lucida Sans Unicode", "Lucida Sans", "Lucida Console",  monospace;
    font-size: 14px;
    line-height: 20px;
    }

    .table{ border-collapse:collapse; border:solid 1px gray; padding:6px}
    .table td{border:solid 1px gray; padding:6px}

    .color-ok {color: green;}
    .color-warning {color: coral;}
    .color-error {color: red;}

    .bg-ok {background-color: lavender;}
    .bg-warning {background-color: yellow;}
    .bg-error {background-color: deeppink;}
    </style>"""
    msg_head = """<html><head><meta charset="utf-8"></head>""" + msg_style + "<body>"
    msg = msg_head + """<h2>{}</h2>""".format(header)
    msg = msg + content + "</body></html>"
    msg = msg.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
    return msg


def run_monitor():
    # monitor = threading.Thread(target=task)
    # monitor.start()
    # monitor2 = threading.Thread(target=task2)
    # monitor2.start()
    monitor = threading.Thread(target=momo, name='2', args=(2, 60))
    monitor1 = threading.Thread(target=momo, name='100', args=(100, 3))
    monitor.start()
    monitor1.start()

if __name__ == "__main__":
    run_monitor()