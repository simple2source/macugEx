# coding:utf8

import os,sqlite3,datetime,time
from common import *
import disk2
from prettytable import PrettyTable
import sys
from show_mysql import *


def get_restult(moudle_name='',database_path=''):
    '''功能描述：依次读取总数、昨天总数、今天总数、一个小时内总数、五分钟内总数。'''
    try:
        if moudle_name and os.path.isfile(database_path):
            total_num=0
            last_day_num=0
            today_num=0
            lasthour_num=0
            lastfivemin_num=0

            con = sqlite3.connect(database_path)
            cur = con.cursor()                       
            yestorday_str = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            today_str = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
            onehour_before = (datetime.datetime.now()-datetime.timedelta(seconds=3600)).strftime('%Y-%m-%d %H:%M:%S')
            fivemin_before = (datetime.datetime.now()-datetime.timedelta(seconds=300)).strftime('%Y-%m-%d %H:%M:%S')
            if moudle_name == 'cjolsearch':
                cur.execute('select total from total_count where moudle ="%s"' % moudle_name)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        total_num = data[0][0] 
                except:
                    pass
                    
                cur.execute('select sum(num) from cjolsearch_seg_count where update_at >"%s" and update_at < "%s"' % (yestorday_str,today_str))
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        last_day_num = data[0][0]
                except:
                    pass
                
                cur.execute('select sum(num) from cjolsearch_seg_count where update_at > "%s"' % today_str)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        today_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from cjolsearch_seg_count where update_at > "%s"' % onehour_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lasthour_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from cjolsearch_seg_count where update_at > "%s"' % fivemin_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lastfivemin_num = data[0][0]
                except:
                    pass

            if moudle_name == '51search':
                cur.execute('select total from total_count where moudle ="%s"' % moudle_name)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        total_num = data[0][0]
                except:
                    pass

                cur.execute('select sum(num) from job51search_seg_count where update_at >"%s" and update_at < "%s"' % (yestorday_str,today_str))
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        last_day_num = data[0][0]
                except:
                    pass

                cur.execute('select sum(num) from job51search_seg_count where update_at > "%s"' % today_str)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        today_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from job51search_seg_count where update_at > "%s"' % onehour_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lasthour_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from job51search_seg_count where update_at > "%s"' % fivemin_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lastfivemin_num = data[0][0]
                except:
                    pass

            if moudle_name == 'zhilian':
                cur.execute('select total from total_count where moudle ="%s"' % moudle_name)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        total_num = data[0][0]
                except:
                    pass

                cur.execute('select sum(num) from zhilian_seg_count where update_at >"%s" and update_at < "%s"' % (yestorday_str,today_str))
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        last_day_num = data[0][0]
                except:
                    pass

                cur.execute('select sum(num) from zhilian_seg_count where update_at > "%s"' % today_str)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        today_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from zhilian_seg_count where update_at > "%s"' % onehour_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lasthour_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from zhilian_seg_count where update_at > "%s"' % fivemin_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lastfivemin_num = data[0][0]
                except:
                    pass

            if moudle_name == 'cjol':
                cur.execute('select total from total_count where moudle ="%s"' % moudle_name)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        total_num = data[0][0] 
                except:
                    pass
                    
                cur.execute('select sum(num) from cjol_seg_count where update_at >"%s" and update_at < "%s"' % (yestorday_str,today_str))
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        last_day_num = data[0][0]
                except:
                    pass
                
                cur.execute('select sum(num) from cjol_seg_count where update_at > "%s"' % today_str)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        today_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from cjol_seg_count where update_at > "%s"' % onehour_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lasthour_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from cjol_seg_count where update_at > "%s"' % fivemin_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lastfivemin_num = data[0][0]
                except:
                    pass

            if moudle_name == '51job' or moudle_name == 'job51':
                cur.execute('select total from total_count where moudle ="51job"')
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        total_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from job51_seg_count where update_at >"%s" and update_at < "%s"' % (yestorday_str,today_str))
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        last_day_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from job51_seg_count where update_at > "%s"' % today_str)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        today_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from job51_seg_count where update_at > "%s"' % onehour_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lasthour_num = data[0][0]
                except:
                    pass
                cur.execute('select sum(num) from job51_seg_count where update_at > "%s"' % fivemin_before)
                data=cur.fetchall()
                try:
                    if data[0][0] >0:
                        lastfivemin_num = data[0][0]
                except:
                    pass
            con.close()
        return [total_num,last_day_num,today_num,lasthour_num,lastfivemin_num]
    except Exception,e:
        return []


def result_print(moudle_list=[],dbfile=''):
    '''功能描述：将数据库查询结果进行打印输出'''
    try:
        for item in moudle_list:
            if item and dbfile:
                try:
                    result=get_restult(item,dbfile)
                    print '数据源名称 '+item+" 简历总数：%d 昨天总数：%d 今天总数：%d 近一个小时：%d 近五分钟：%d "%(result[0],result[1],result[2],result[3],result[4])
                except Exception,e:
                    pass
        try:
            if disk2.bakinfo():
                bakmsg = '备份脚本正在运行'
            else:
                bakmsg = '备份脚本暂未运行'
            print bakmsg
            dbcountmsg = disk2.ex_msg('all')[0]
            print dbcountmsg
            new_db_msg = disk2.ex_msg('new_all')[0]
            print new_db_msg
            cjol_db_msg = disk2.ex_msg('cjol')[0]
            print cjol_db_msg
            job51_db_msg = disk2.ex_msg('51job')[0]
            print job51_db_msg
            zhilian_db_msg = disk2.ex_msg('zhilian')[0]
            print zhilian_db_msg
        except Exception,e:
            pass
        try:
            # m_list = msg_list()
            # m_l = []
            # for m in m_list:
            #     m_l.append(get_msg(m)[1])
            # mysql_msg = ''
            # for mm in m_l:
            #     mysql_msg += mm
            mysql_msg = html_create()[1]
            print(mysql_msg)
        except:
            pass
        return True
    except Exception,e:
        return False


def autologin_result(module='', dbfile=''):
    try:
        db = sqlite3.connect(dbfile)
        today_str = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
        cur = db.cursor()
        # select all username
        cur.execute('select distinct(username) from {}'.format(module))
        data = cur.fetchall()
        user_list = []
        for i in data:
            user_list.append(i[0])
        x = PrettyTable([u"用户名",u"登录次数",u"重试总数"])
        x.align[u"用户名"] = "l"
        for i in user_list:
            cur.execute('select * from {} where add_time > "{}" and username="{}" '.format(module, today_str, i.encode('utf-8')))
            data1 = cur.fetchall()
            day_times = len(data1)   # 一天内尝试的次数
            cur.execute('select sum(times) from {} where add_time > "{}" and username="{}"'.format(module, today_str, i.encode('utf-8')))
            data = cur.fetchall()
            try:
                day_try_count = data[0][0]  #　一天内所有的重试次数，更尝试次数可以比较
            except:
                day_try_count = 0
            x.add_row([i.encode('utf-8'), day_times, day_try_count])
        db.close()
        x_str = x.get_html_string(sortby=u'登录次数', reversesort=True).encode('utf-8')
        rep_list = ['<td>' + str(x) + '</td>' for x in xrange(5, 50)]
        for i in rep_list:
            x_str = x_str.replace(i, i.replace('<td>', '<td style="color:red; text-align:right">'))
        #print x.get_html_string().encode('utf-8')
        #return x.get_html_string().encode('utf-8')
        return x_str
    except Exception, e:
        print Exception, e
        return None


def result_email(moudle_list=[],dbfile=''):
    '''功能描述：将数据库查询结果以邮件方式发送
    #改成 return Email内容，方便分技术与非技术报表 '''
    try:
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
        msg = msg_head + """<h2>抓取数据报表</h2>"""
        x = PrettyTable(["来源","总数","昨天","今天","近1h","近5min"])
        x.align["来源"] = "l"
        x.padding_width = 10
        try:
            redis_res = disk2.redis_info()
            if int(redis_res) > 10000:
                redis_res = '<span style="color:red">' + redis_res + '</span>'
            rmsg = '<br><br> Redis 队列里堵塞的数据量 {}'.format(redis_res)
        except Exception, e:
            rmsg = ''
            print Exception, e
        try:
            dresult = disk2.diskinfo('data')
            dleft = dresult[2].strip()
            if float(dleft[:-1]) <= 50:
                dleft = '<span style="color:red">' + dleft + '</span>'
            dmsg = '<br>磁盘信息   总空间: ' + dresult[0]  + ' 剩余: ' + dleft + ' 使用百分比: ' + dresult[3]
        except Exception, e:
            print Exception, e
            dmsg = ''
        if disk2.bakinfo():
            bakmsg = '<br><br>备份脚本正在运行'
        else:
            bakmsg = '<br><br>备份脚本暂未运行'
        #x.border = True
        for item in moudle_list:
            if item and dbfile:
                try:
                    result = get_restult(item,dbfile)
                    if item == '51job':
                        result[0] += 5379298
                    if item == 'cjol':
                        result[0] = 5615513
                    #print result
                    x.add_row([item,result[0],result[1],result[2],result[3],result[4]])
                except Exception,e:
                    pass
        xcontent = x.get_html_string()
        msg = msg + dmsg + rmsg + bakmsg + '<br><br>' + '-'*20 + '<br><h2>sqlite统计</h2>' + xcontent.encode('utf8')
        msg2 = '<br>注：cjolsearch,job51search,zhilian 为通过搜索下载最新简历，\
        <br>可能与之前cjol,51job遍历简历ID下载的重复，以后会统一<br>'
        msg = msg + msg2

        # if disk2.bakinfo():
        #     bakmsg = '<br><br>备份脚本正在运行'
        # else:
        #     bakmsg = '<br><br>备份脚本暂未运行'
        try:
            x2 = PrettyTable(["来源", "昨天", "今天", "增量"])
            x2.align["来源"] = "l"
            x2.padding_width = 10
            m_list = ['all', 'new_all', 'zhilian', 'cjol', '51job']
            for m in m_list:
                x2.add_row([m, disk2.ex_msg(m)[1], disk2.ex_msg(m)[2], disk2.ex_msg(m)[3]])
            x2content = '<br><h2>入搜索库统计</h2><br>' + x2.get_html_string().encode('utf8')
        except:
            # print x2content
            x2content = ''

        login51_html = autologin_result('job51', stat_db_path)
        if not login51_html:
            login51_html = ''

        # dbcountmsg = disk2.ex_msg('all') + '<br>'
        # new_db_msg = disk2.ex_msg('new_all') + '<br>'
        # cjol_db_msg = disk2.ex_msg('cjol') + '<br>'
        # job51_db_msg = disk2.ex_msg('51job') + '<br>'
        # zhilian_db_msg = disk2.ex_msg('zhilian') + '<br>'

        msg_divide = '''<br>------------------------<br><br>下面是MySQL统计表格<br>
                     51search, zhilian, cjol 为最新搜索下载的统计，用户名（ext1）,状态（ext2）<br>
                     带seg 的为入库统计，状态（ext2）<br>
                     login, order, auth, reg 为web端统计， 来源（ext1）<br>'''
        # m_list = msg_list()
        # m_l = []
        # for m in m_list:
        #     m_l.append(get_msg(m)[0])
        # mysql_msg = ''
        # for mm in m_l:
        #     mysql_msg += mm

        mysql_msg5 = html_create()[0]

        # msg = msg + dmsg + login51_html + x2content + bakmsg + msg_divide + mysql_msg5 + "</body></html>"
        msg = msg + login51_html + x2content + msg_divide + mysql_msg5 + "</body></html>"
        # msg = msg.replace('<table>', '<table border="1">').replace('<td>', '<td style="text-align:right">')
        msg = msg.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
        #print msg

        #sendEmail('default_main', '抓取数据报告', msg,msg_type=1)
        #return True
        return msg
    except Exception,e:
        print Exception, e
        return False


def show_process_count(task_name):
    # 查询每个进程对应的单位时间内的抓取量
    try:
        conn = sqlite3.connect('/data/fetch/database/process_fetch.db')
        result_dict = {'task_name': '', 'yesterday': {'ok': 0, 'remove': 0},
                       'today': {'ok': 0, 'remove': 0}, 'hour': {'ok': 0, 'remove': 0},
                       'minute': {'ok': 0, 'remove': 0}}
        cur = conn.cursor()
        yesterday = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
        one_hour_before = (datetime.datetime.now()-datetime.timedelta(seconds=3600)).strftime('%Y-%m-%d %H:%M:%S')
        five_min_before = (datetime.datetime.now()-datetime.timedelta(seconds=300)).strftime('%Y-%m-%d %H:%M:%S')
        yesterday_sql = "SELECT sum(ok),sum(remove) from process_fetch_count " \
                        "WHERE at_time > '{}' and at_time < '{}' and task_name='{}'".format(yesterday, today, task_name)
        today_sql = "SELECT sum(ok),sum(remove) from process_fetch_count " \
                    "WHERE at_time > '{}'".format(today)
        one_hour_sql = "SELECT sum(ok),sum(remove) from process_fetch_count " \
                       "WHERE at_time > '{}'".format(one_hour_before)
        five_min_sql = "SELECT sum(ok),sum(remove) from process_fetch_count " \
                       "WHERE at_time > '{}'".format(five_min_before)
        cur.execute(yesterday_sql)
        result_dict['yesterday']['ok'] = cur.fetchall()[0][0]
        result_dict['yesterday']['remove'] = cur.fetchall()[0][-1]
        cur.execute(today_sql)
        result_dict['today']['ok'] = cur.fetchall()[0][0]
        result_dict['today']['remove'] = cur.fetchall()[0][-1]
        cur.execute(one_hour_sql)
        result_dict['hour']['ok'] = cur.fetchall()[0][0]
        result_dict['hour']['remove'] = cur.fetchall()[0][-1]
        cur.execute(five_min_sql)
        result_dict['minute']['ok'] = cur.fetchall()[0][0]
        result_dict['minute']['remove'] = cur.fetchall()[0][-1]
        result_dict['task_name'] = task_name
        print result_dict
        return result_dict
    except Exception, error:
        print error


if __name__ == '__main__':
    '''将之前viewstat 的功能移到这里，不需要viewstat'''
    print 'test...'
    #result_print(['cjol','51job'],database_path)
    #result_email(['cjol','51job'],database_path)

    para=''
    try:
        para=sys.argv[1]
    except:
        pass
    result_print(['cjol','cjolsearch','51job','51search','zhilian'],database_path)
    if para == 'mail':
        msg = result_email(['cjol','cjolsearch','51job','51search','zhilian'],database_path)
        sendEmail('default_main', '报表03: 抓取数据统计', msg,msg_type=1)
        # print msg
        print 'sent Technich email'
    if para == 'pmail':
        msg = result_email(['cjol','cjolsearch','51job','51search','zhilian'],database_path)
        #print msg
        sendEmail('default_main', '报表03: 抓取数据统计', msg,msg_type=1, des='P')
        print 'sent Product email'

    

