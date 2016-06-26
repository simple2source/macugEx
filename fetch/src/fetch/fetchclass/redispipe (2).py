# encoding=utf-8

'''在爬虫模块中引入这个脚本，然后 tranredis(msgtype,num)即可，
cjolsearch例子，tranrdies(cjolsearch_success,num)，tranrdies(cjolsearch_needlogin,num)，
rcheck 为检查redis 里面有没有改简历ID, expired_day 是过期时间，大于该时间更改该ID存储的时间
'''
## todo 重构代码，增加注释
import redis, time, datetime,json, random, os
from log import *
import sqlite3, MySQLdb

class Db(object):
    """handle mysql gone away gracefully"""
    def __init__(self):
        self.sql_config = {
            'host': "localhost",
            'user': "testuser",
            'passwd': "",
            'db': 'reportdb',
            'charset': 'utf8',
        }
        # self.sql_config = {
        #     'host': "10.4.14.233",
        #     'user': "tuike",
        #     'passwd': "sv8VW6VhmxUZjTrU",
        #     'db': 'tuike'
        # }


class Rdsreport(object):
    def __init__(self):
        ## 在这里增加config 216上面为localhost，其他机器用此脚本需要改host 为 10.4.10.77
        self.config={
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            #'connection_pool': self.pool
        }
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.not_write_path = os.path.join(self.path, 'not_write_in_redis.txt')
        self.error_path = os.path.join(self.path, 'redis_error.txt')
        self.pool = redis.ConnectionPool(**self.config)
        self.r = redis.StrictRedis(connection_pool=self.pool, **self.config)
        # self.r = redis.StrictRedis(**self.config)
        # self.sql_config = {
        #     'host': "localhost",
        #     'user': "testuser",
        #     'passwd': "",
        #     'db': 'reportdb'
        # }
        self.sql_config = {
            'host': "10.4.14.233",
            'user': "tuike",
            'passwd': "sv8VW6VhmxUZjTrU",
            'db': 'tuike',
            'charset': 'utf8',
        }
        # self.db = MySQLdb.connect(**self.sql_config)
        # self.cursor = self.db.cursor()

    def redisavail(self,redis_instant):
        '''检查 redis 服务状态，等待上线'''
        while 1:
            try:
                if redis_instant.ping():
                    return True
            except Exception, e:
                logging.warning('redis off line')
                timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                error_text = timenow + str(e) + '\n'
                with open(self.error_path, 'a+') as f:
                    f.write(error_text)

            time.sleep(5)


    def tranredis(self,msgtype , num, **kwargs):
        '''传输数据到redis'''
        while 1:
            # r = redis.StrictRedis(**self.config)
            timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            info = {'msgtype': msgtype, 'time':timenow, 'num':num}
            info.update(kwargs)
            traninfo = json.dumps(info)
            # print traninfo
            try:
                self.r.lpush('queue',traninfo)
                try:
                    # 不要阻止爬虫运行， 每次写50条
                    n = 0
                    while n < 50:
                        with open(self.not_write_path, 'a+') as f:
                            lines = f.readlines()
                        if len(lines) > 0:
                            self.r.lpush('queue',lines[0])
                            with open(self.not_write_path, 'w') as f:
                                for line in lines[1:]:
                                    f.write(line)
                        n += 1
                    else:
                        break
                except Exception, e:
                    print Exception, str(e)
            except:
                with open(self.not_write_path, 'a+') as f:
                    traninfo_text = str(traninfo) + '\n'
                    f.write(traninfo_text)


    def redishandle(self):
        '''从redis得到数据'''
        # pool = redis.ConnectionPool(**self.config)
        # r = redis.StrictRedis(connection_pool=pool)
        self.redisavail(self.r)
        result = self.r.brpop('queue', 0)[1]
        #jsonstring = json.dumps(result)
        # print result
        try:
            s = json.loads(result)
            # for key in s:
            #     print key
            #     msgtype, trantime, num  = key, s[key][0]['time'], s[key][0]['num']
            try:
                msgtype, trantime, num = s['msgtype'], s['time'], int(s['num'])

                timelist = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
                # 5分钟的时间间隔
                # timelist = filter(lambda x: x % 5 == 0, range(61))
                trantimeobj = datetime.datetime.strptime(trantime, '%Y-%m-%d %H:%M:%S')
                statmin = trantimeobj.minute
                for l in timelist:
                    index = timelist.index(l)
                    if timelist[index]<= statmin < timelist[index+1]:
                        statmin = timelist[index]
                statimeobj = trantimeobj.replace(minute=statmin, second=0)
                #msgtype = random.choice(['cjolsearch_success','cjolsearch_needlogin', 'cjolsearch_attachement'])
                s['time'] = statimeobj
                # return [statimeobj, msgtype ,num]
                # print s
                return s
            except Exception, e:
                logging.warning('{} format is not correct and error msg is {}'.format(s, str(e)))
                return None
        except Exception, e:
            logging.warning('error msg is {}'.format(str(e)))
            return None

    def mysql_connect(self):
        try:
            self.db = MySQLdb.connect(**self.sql_config)
        except:
            print 'wait 60s to connect mysql '
            time.sleep(60)
            self.mysql_connect()
        return True

    def mysql_reconnect(self):
        # if 'db' not in locals():
        #     self.db = MySQLdb.connect(**self.sql_config)
        try:
            self.db.ping()
            self.cursor = self.db.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            print 'reconecting'
            self.mysql_connect()
            self.mysql_reconnect()
        return True


    def mysqlhandle(self):
        '''从redis handle 得到 statimeobj, msgtype ,num， while 循环写入mysql'''
        # try:
        #     db = MySQLdb.connect(**self.sql_config)
        #     cursor = db.cursor()
        # except (AttributeError, MySQLdb.OperationalError):
        #     print 'lost connect with MySQL'
        #     db = MySQLdb.connect(**self.sql_config)
        self.mysql_connect()
        self.mysql_reconnect()
        while 1:
            redisresult = self.redishandle()
            if redisresult:
                # print redisresult
                statimeobj = redisresult['time']
                msgtype = redisresult['msgtype']
                num = redisresult['num']
                ext1 = redisresult.pop('ext1', '').encode('uft-8')
                ext2 = redisresult.pop('ext2', '')
                ext3 = redisresult.pop('ext3', '')
                # statimeobj, msgtype ,num = redisresult[0], redisresult[1], redisresult[2]

                sql_up = """update stats set num=num+{}, add_time=now() where msgtype ="{}"
                            and stat_time ="{}" and ext1 = "{}" and ext2 = "{}" and ext3 = "{}"
                            limit 1;
                            """.format(num, msgtype, statimeobj, ext1, ext2, ext3)   # ORDER BY id DESC
                sql_in = """insert into stats (stat_time, add_time, num, msgtype,ext1,ext2,
                            ext3) values ("{}", now(), "{}", "{}", "{}", "{}", "{}")
                            """.format(statimeobj, num, msgtype,  ext1, ext2, ext3)
                # sql_sel = """ select `id` from stats  where msgtype ="{}"
                #             and stat_time ="{}" and ext1 = "{}" and ext2 = "{}" and ext3 = "{}";
                #             """.format(msgtype, statimeobj, ext1, ext2, ext3)
                try:
                    # db = MySQLdb.connect("localhost","testuser","","reportdb" )
                    # db = MySQLdb.connect("10.4.14.233","tuike","sv8VW6VhmxUZjTrU","tuike" )
                    #db = sqlite3.connect('report.db')
                    try:
                        b = self.cursor.execute(sql_up)
                        self.db.commit()
                        if b == 0L:
                            try:
                                c = self.cursor.execute(sql_in)
                                self.db.commit()
                            except:
                                self.db.rollback()
                    except(AttributeError, MySQLdb.OperationalError):
                        self.db.rollback()
                        print 'lost connect with MySQL'
                        # db = MySQLdb.connect(**self.sql_config)
                        # cursor = db.cursor()
                        self.mysql_reconnect()
                        pass
                    # db.close()
                except (AttributeError, MySQLdb.OperationalError):
                    # db = MySQLdb.connect(**self.sql_config)
                    # cursor = db.cursor()
                    self.mysql_reconnect()
                    pass

    def rcheck(self, resumeid, addtime, expired_day=2):
        '''
        增加 redis 存储简历ID ，并监测更新时间，大于两天覆盖更新原简历
        默认格式为 key: cj_ + id  addtime 时间格式为 '%Y-%m-%d %H:%M:%S'
        expeired_day 为过期时间， 大于?天返回false，并更新redis中时间，默认两天
        不操作 key 对应时间，对应时间在 es_add 中增加
        '''
        r = redis.StrictRedis(**self.config)
        try:
            if r.exists(resumeid):
                addtimeobj = datetime.datetime.strptime(addtime, '%Y-%m-%d %H:%M:%S')
                r_result = r.get(resumeid).split(',')
                addtimebefore = r_result[0]
                # if len(r_result) > 2:
                #     es_result = r_result[1]
                # else:
                #     es_result = '0'
                addtimebefore = datetime.datetime.strptime(addtimebefore, '%Y-%m-%d %H:%M:%S')
                if addtimeobj - addtimebefore >= datetime.timedelta(days=expired_day):
                    # r.set(resumeid,addtime)  # 在检查有没入库的时候更新 addtime 注释这句
                    logging.info( '%s 已经 %s 天没更新了' % (resumeid, expired_day))
                    return True
                else:
                    logging.info( '%s %s 天内多次更新' % (resumeid, expired_day))
                    return False
            else:
                logging.info( '%s not exist in redis' % resumeid)
                r.set(resumeid,addtime)
                return True
        except Exception, e:
            print Exception, str(e)
            logging.warning('Check  %s id in redis error ,and error msg is %s' % (resumeid, str(e)))
            return False

    def es_add(self, resumeid, addtime, status):
        """增加入库状态 0 或 1"""
        r = redis.StrictRedis(**self.config)
        if isinstance(status, int):
            # r_result = r.get(resumeid).split(',')
            r_string = str(addtime) + ',' + str(status)
            r.set(resumeid, r_string)
        else:
            logging.info('%s id status code format not right!' % resumeid)

    def testes_add(self):
        """测试用，从es数据库中导入，增加入库状态 1"""
        r = redis.StrictRedis(**self.config)
        i = 1
        with open('/data/51_extracted/source_id.txt') as f:
            for line in f:
                l = line.split(' ')
                source = l[0]
                resumeid = l[1].strip()
                if source == '51job':
                    resumeid = 'wu_' + resumeid
                elif source == 'zhilian':
                    resumeid = 'z_' + resumeid
                elif source == 'cjol':
                    resumeid = 'c_' + resumeid
                if r.exists(resumeid):
                    r_result = r.get(resumeid).split(',')
                    addtime = r_result[0]
                    r_string = str(addtime) + ',' + str(1)
                    r.set(resumeid, r_string)
                else:
                    logging.info('%s id not in redis!' % resumeid)
                i += 1
                if i % 1000 == 0:
                    print '1000 id done'

    def es_check(self, resumeid):
        """检查 es入库状态 返回值 0不在库中，1在库中"""
        r = redis.StrictRedis(**self.config)
        r_result = r.get(resumeid).split(',')
        if len(r_result) > 1:
            es_result = int(r_result[1])
        else:
            es_result = 0
        return es_result

    def check(self,resumeid):
        r = redis.StrictRedis(**self.config)
        # self.redisavail()
        if r.exists(resumeid):
            return True
        else:
            return False


    def test(self):
        r = redis.StrictRedis(**self.config)
        return r

if __name__ == '__main__':
    r = Rdsreport()
    r.mysqlhandle()
