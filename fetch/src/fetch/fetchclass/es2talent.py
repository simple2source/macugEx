# -*- coding: UTF-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
from elasticsearch import Elasticsearch
import chardet
from prettytable import PrettyTable
import urllib
import urllib2
import re
import time, json
import datetime
import oldmysql
import random


def test3(key_word):
    es = Elasticsearch("183.131.144.102:8090")
    size = 20
    query_key = "work_experience.seged_job_name"
    query_value = key_word.lower()
    today_str = str(datetime.datetime.today().date())
    #print today_str
    res = es.search(index='supin_resume', doc_type='doc_v1', # explain=True,  #_source_include=["work_experience.job_name" , "resume_update_time"],
                    body={   # , "resume_update_time"
                        # "_source": ["work_experience.seged_job_name", 'resume_update_time'],
            "query": {
                "bool": {
                    "must": [
                        {"match":
                            {
                                "work_experience.job_name": {"query": query_value} #, "operator": "and", "type": "phrase"},
                            }
                        },
                        {"match":
                            {
                                "work_experience.job_describe": {"query": query_value}

                            }
                        },
                        {"match":
                            {
                                "resume_update_time": {"query": today_str}

                            }
                        }
                    ]
                }
            # }
            }, "size": size
        }
                    )
    #print res
    #print len(res['hits']['hits'])
    #print json.dumps(res['hits']['hits'][0])
    return res


def info_fliter(d):
    # 将返回来的json 提取需要使用的信息
    pass

def insert_mysql(d):
    # 插入到MySQL
    sql_config = {
        'host': "10.4.14.233",
        'user': "tuike",
        'passwd': "sv8VW6VhmxUZjTrU",
        'db': 'tuike',
        'charset': 'utf8'
    }

def main(keywword, category):
    res = test3(key_word=keywword)
    j_dict = res['hits']['hits']
    rand_count = random.choice(range(1,6))
    print rand_count
    j2_dict = random.sample(j_dict, rand_count)
    print j2_dict
    print len(j2_dict)
    for i in j2_dict:
        i = i['_source']
        # print i
        self_describe = i.get('self_evaluation', '')
        if len(self_describe) > 0:
            source = i['source']
            old_sql = oldmysql.OldMysql(source, i, category)
            old_sql.run_work()

if __name__ == '__main__':
    ll = ['php', 'c++', u'前端', u'安卓 android', u'ios', 'java', u'设计', u'.net开发 数据分析 python开发 运维',
          u'产品经理 运营经理', u'人事 招聘经理 招聘专员']
    for i in range(0, 10):
        main(ll[i], i+1)
    main(u'策划 市场推广', 12)
    main(u'测试', 14)
