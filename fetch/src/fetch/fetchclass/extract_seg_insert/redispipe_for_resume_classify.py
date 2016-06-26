# encoding=utf-8

import sys, redis, datetime, json, time, os, traceback
reload(sys)
sys.setdefaultencoding('utf8')
# sys.path.append('/data/fetch_git/fetch/src/fetch/fetchclass')
# sys.path.append('..')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from log import *
import common
import logging
import logging.config
from elasticsearch import Elasticsearch
# sys.path.append('/data/fetch_git/fetch/src/fetch/fetchclass/extract_seg_insert/libs/Search-module/rss')
# sys.path.append('./libs/Search-module/rss')
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs', 'Search-module', 'rss'))
from resume_classify import resume_classify

class ResumeClassifyPipe(object):
    def __init__(self):
        # 配置redis服务器地址，216上面为localhost，其他机器用此脚本需要改host为
        # 10.4.10.77
        self.config = {
            'host' : 'localhost',
            'port' : 6379,
            'db' : 0,
        }

        # 配置日志
        self.format = '[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d][%(levelname)s]:%(message)s'
        self.logger = logging.getLogger(__name__)
        fh = logging.FileHandler(os.path.join(log_dir,\
            'redispipe_for_resume_classify.log'))
        formatter = logging.Formatter(fmt=self.format)
        fh.setFormatter(formatter)
        self.logger.handlers = [fh]

        # redis未启动时临时存储队列信息的文件路径
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.temp_path = os.path.join(self.path, 'msg_not_in_redis.txt')
        self.error_path = os.path.join(self.path, 'redis_error.txt')

        # redis连接池和连接实例
        self.pool = redis.ConnectionPool(**self.config)
        self.r = redis.StrictRedis(connection_pool=self.pool, **self.config)

        # 队列名
        self.queue_name = 'resume_classify_queue'

        # es库连接
        self.es = Elasticsearch('10.4.29.242:8090')
        # self.es = Elasticsearch('127.0.0.1:9200')

    def redis_avail(self, redis_instant):
        '''检查 redis 服务状态，等待上线'''
        while 1:
            try:
                if redis_instant.ping():
                    return True
            except Exception, e:
                self.logger.warning('redis off line.')
                timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                error_text = timenow + str(e) + '\n'
                with open(self.error_path, 'a+') as f:
                    f.write(error_text)

            time.sleep(5)

    def producer(self, resume_id):
        '''输入数据到 redis 消息队列'''
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg_dict = {'resume_id' : resume_id, 'time' : time_now}
        msg_str = json.dumps(msg_dict)
        print msg_str
        try:
            self.r.lpush(self.queue_name, msg_str)
            self.logger.info('push succ. msg:%s' % msg_str)
        except Exception, e:
            err_str = traceback.format_exc()
            print err_str
            self.logger.error(err_str)
            self.logger.info('write msg to redis fail.')
            # 消息写入redis失败，临时写入文件中保存
            with open(self.temp_path, 'a') as f:
                f.write(msg_str + '\n')

    def consumer(self):
        '''从 redis 队列获取消息，根据消息中的简历id从es库获取简历，对简历进行
        分类，然后把分类结果更新到es库'''

        while 1:
            # 验证 redis 服务器正在运行
            self.redis_avail(self.r)

            # 如果消息队列长度小于5，跳过此次循环。预留es库同步数据的时间
            msg_count = self.r.llen(self.queue_name)
            if msg_count <= 5:
                continue

            # 从 redis 队列取消息
            msg_str = self.r.brpop(self.queue_name, 0)[1]
            self.logger.info('get msg succ. msg:%s' % msg_str)
            msg_dict = json.loads(msg_str)

            # 从 es 库查询简历
            resume_id = msg_dict['resume_id']
            res = self.get_resume_from_es(resume_id)

            if res:
                if res['hits']['total'] > 0:
                    for item in res['hits']['hits']:
                        es_id = item['_id']
                        resume_dict = item['_source']
                        classify_result = self.resume_classify(es_id,
                            resume_dict)
                        if classify_result:
                            self.logger.info('resume classify succ. es_id:%s, \
                                resume_id:%s' % (es_id, resume_id))
                        else:
                            self.logger.info('resume classify fail. es_id:%s, \
                                resume_id:%s' % (es_id, resume_id))
                else:
                    self.logger.info('total equals 0. resume_id:%s' % resume_id)
                    # total为0的msg写到临时存储文件，尝试下次分类
                    with open(self.temp_path, 'a') as f:
                        f.write(msg_str + '\n')
            else:
                self.logger.info('get resume from es fail.resume_id:%s' % resume_id)

    def get_resume_from_es(self, resume_id):
        '''根据 resume_id 从 es 库查询简历'''
        query_dsl = {
            'query' : {
                'bool' : {
                    'must' : [
                        {'match' : {'id' : resume_id}}
                    ]
                }
            }
        }
        try:
            res = self.es.search(index='supin_resume_v1', doc_type='doc_v1',\
                                 body=query_dsl)
            return res
        except Exception, e:
            err_str = traceback.format_exc()
            print err_str
            self.logger.error(err_str)
            return None

    def resume_classify(self, es_id, resume_dict):
        '''对简历进行分类操作，并将结果更新到 es 库'''
        if 'work_experience' in resume_dict:
            # 为简历中的每一份工作经历添加类别
            try:
                for experience_dict in resume_dict['work_experience']:
                    # 分别判断当前工作经历是否属于第n类
                    category_list = []
                    for i in range(1, 13):
                        category = int(resume_classify(i, experience_dict))
                        if category == 1:
                            category_list.append(i)
                    if len(category_list) == 0:
                        category_list.append(13)
                    experience_dict['job_category'] = category_list
                    # with open('fetch_do123.log', 'a') as f:
                    #     json.dump(experience_dict, f, ensure_ascii=False)
                    #     f.write('\n')
            except Exception, e:
                err_str = traceback.format_exc()
                print err_str
                self.logger.error(err_str)
                return 0
            # 把分类结果更新到 es 库
            try:
                update_result = self.es.update(index='supin_resume_v1',\
                    doc_type='doc_v1', id=es_id, body={'doc' : resume_dict})
                if update_result['_shards']['successful'] == 1 and \
                    update_result['_version'] > 1:
                    return 1
                else:
                    return 0
            except Exception, e:
                err_str = traceback.format_exc()
                print err_str
                self.logger.error(err_str)
                self.logger.info('update resume fail. es_id:%s, resume_id:%s'\
                             % (es_id, resume_dict['id']))
                return 0
        else:
            self.logger.info('work_experience is null. es_id:%s, resume_id:%s'\
                         % (es_id, resume_dict['id']))
            return 1

    def push_old(self):
        '''把redis未启动时临时存储在文件的消息重新推送到redis'''
        while 1:
            # 验证 redis 服务器正在运行
            self.redis_avail(self.r)

            try:
                n = 0
                while n < 50:
                    with open(self.temp_path, 'a+') as f:
                        lines = f.readlines()
                    if len(lines) > 0:
                        line = lines[0].replace('\n', '')
                        self.r.lpush(self.queue_name, line)
                        self.logger.info('push old succ. msg:%s' % line)
                        with open(self.temp_path, 'w') as f:
                            for line in lines[1:]:
                                f.write(line)
                    n += 1

                time.sleep(10)
            except Exception, e:
                err_str = traceback.format_exc()
                print err_str
                self.logger.error(err_str)
                self.logger.info('push temp save msg fail.')

if __name__ == '__main__':
    r = ResumeClassifyPipe()
    arg = sys.argv[1]
    if arg == 'consume':
        r.consumer()
    elif arg == 'push_old':
        r.push_old()
    else:
        print 'argv[1] wrong.'