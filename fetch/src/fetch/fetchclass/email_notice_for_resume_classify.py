# encoding:utf8

import sys, os, datetime, redis
import common

reload(sys)
sys.setdefaultencoding('utf8')

# redis服务器地址，216上面为localhost，其他机器用此脚本需要改host为
# 10.4.10.77
host = 'localhost'
port = 6379
db = 0

queue_name = 'resume_classify_queue'

def main():
    '''统计简历分类消息队列中的消息数'''

    msg = '<p>当前时间：</p>'

    # 当前时间
    now = datetime.datetime.now()
    msg += '<p>%s</p>' % now

    # 获取当前队列中的消息数
    redis_instant = redis.StrictRedis(host=host, port=port, db=db)
    if redis_instant.ping():
        msg_count = redis_instant.llen(queue_name)
        tmp_msg = '<p>消息队列长度：%s</p>' % msg_count
    else:
        '<p>redis未启动</p>'

    msg += tmp_msg
    print msg

    # 发送邮件
    title = '简历分类-消息队列长度监测'
    common.sendEmail(title=title, message=msg)

if __name__ == '__main__':
    main()