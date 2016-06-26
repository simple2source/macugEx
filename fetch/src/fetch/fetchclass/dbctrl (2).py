#-*- coding:UTF-8 -*-

from common import database_path
import sqlite3,logging

def data_total_add(moudle_name=''):
    '''功能描述：对于每一种数据源抓取的总数进行记录'''
    try:
        if moudle_name:
            con = sqlite3.connect(database_path)
            cur = con.cursor()
            cur.execute('select count(*) from total_count where moudle = "%s"' % moudle_name)
            data=cur.fetchall()
            if data[0][0] >0:
                cur.execute('update total_count set total = total+1 ,update_at = datetime("now", "localtime") where moudle ="%s"' % moudle_name)
                con.commit()
            else:
                cur.execute('insert into total_count values(NULL,"%s",1,datetime("now", "localtime"))' % moudle_name)
                con.commit()
            con.close()
        return True
    except Exception,e:
        logging.debug('error msg is %s '% str(e))
        return False
    
def data_seg_record(moudle_name='',seg_num = 0,addlist=[]):
    '''功能描述：各个数据源的抓取的分段记录信息保存，记录每段抓取的总数，起始/结束号码以及命中率'''
    try:
        if moudle_name and seg_num:
            if moudle_name == 'cjol':
                con = sqlite3.connect(database_path)
                cur = con.cursor()
                try:
                    begin_num = addlist[0]
                    end_num = addlist[1]
                    get_rate = addlist[2]
                except:
                    begin_num = 0
                    end_num = 0
                    get_rate = 0
                cur.execute('insert into cjol_seg_count values(NULL,%d,datetime("now", "localtime"),%d,%d,%d)' % (seg_num,begin_num,end_num,get_rate))
                con.commit()
                con.close()

            if moudle_name == 'cjolsearch':
                con = sqlite3.connect(database_path)
                cur = con.cursor()
                try:
                    begin_num = addlist[0]
                    end_num = addlist[1]
                    get_rate = addlist[2]
                except:
                    begin_num = 0
                    end_num = 0
                    get_rate = 0
                cur.execute('insert into cjolsearch_seg_count values(NULL,%d,datetime("now", "localtime"),%d,%d,%d)' % (seg_num,begin_num,end_num,get_rate))
                con.commit()
                con.close()

            if moudle_name == '51job':
                con = sqlite3.connect(database_path)
                cur = con.cursor()
                try:
                    begin_num = addlist[0]
                    end_num = addlist[1]
                    get_rate = addlist[2]
                except:
                    begin_num = 0
                    end_num = 0
                    get_rate = 0
                cur.execute('insert into job51_seg_count values(NULL,%d,datetime("now", "localtime"),%d,%d,%d)' % (seg_num,begin_num,end_num,get_rate))
                con.commit()
                con.close()

            if moudle_name == 'zhilian':
                con = sqlite3.connect(database_path)
                cur = con.cursor()
                try:
                    begin_num = addlist[0]
                    end_num = addlist[1]
                    get_rate = addlist[2]
                except:
                    begin_num = 0
                    end_num = 0
                    get_rate = 0
                cur.execute('insert into zhilian_seg_count values(NULL,%d,datetime("now", "localtime"),%d,%d,%d)' % (seg_num,begin_num,end_num,get_rate))
                con.commit()
                con.close()

            if moudle_name == '51search':
                con = sqlite3.connect(database_path)
                cur = con.cursor()
                try:
                    begin_num = addlist[0]
                    end_num = addlist[1]
                    get_rate = addlist[2]
                except:
                    begin_num = 0
                    end_num = 0
                    get_rate = 0
                cur.execute('insert into job51search_seg_count values(NULL,%d,datetime("now", "localtime"),%d,%d,%d)' % (seg_num,begin_num,end_num,get_rate))
                con.commit()
                con.close()
        return True
    except Exception,e:
        logging.debug('error msg is %s' % str(e))
        return False

if __name__ == '__main__':
    print 'db test...'
    data_seg_record('cjol',10,[100,200,2])
    #data_total_add('cjolabc')