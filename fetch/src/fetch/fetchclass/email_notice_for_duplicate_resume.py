# encoding:utf8

import sys, os, datetime
import common

reload(sys)
sys.setdefaultencoding('utf8')

log_file_dict = {'cjol' : 'cjolsearch.log', 'zhilian' : 'zhiliansearch.log',
    'job51_id' : 'job51_id_fetch.log', 'job51_search' : 'job51search.log'}
base_path = '/data/fetch_git/fetch/src/fetch/log'

def log_filter(source):
    '''过滤日志文件，只获得指定的信息。'''

    # 日志内容的时间范围
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    begin_time_str = str(yesterday) + ' 18:00:00,000'
    end_time_str = str(today) + ' 18:00:00,000'

    # 日志路径，输出路径
    log_file_name = log_file_dict[source]
    src_path = os.path.join(base_path, log_file_dict[source])
    des_base_path = '/tmp/teky'
    des_dir = os.path.join(des_base_path, str(today))
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    des_path_false = os.path.join(des_dir, log_file_name+'.false')
    des_path_true = os.path.join(des_dir, log_file_name+'.true')

    # 过滤非重复简历条目
    command = "tail -n 900000 %s | grep 'return False' | awk -F] '$1>=\"[%s\""+\
              " && $1<\"[%s\" {print $0}' > %s"
    os.system(command %(src_path, begin_time_str, end_time_str, des_path_false))

    # 过滤重复简历条目
    command = "tail -n 900000 %s | grep 'return True' | awk -F] '$1>=\"[%s\""+\
              " && $1<\"[%s\" {print $0}' > %s"
    os.system(command %(src_path, begin_time_str, end_time_str, des_path_true))

def get_email_msg():
    '''生成邮件正文'''

    base_path = '/tmp/teky'
    msg = ''

    # 时间范围
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    begin_time_str = str(yesterday) + ' 18:00:00,000'
    end_time_str = str(today) + ' 18:00:00,000'

    msg += '<p>%s 至 %s</p>' % (begin_time_str, end_time_str)

    # 非重复和重复简历数
    for k, v in log_file_dict.items():
        count_false = 0
        des_path_false = os.path.join(base_path, str(today), v+'.false')
        if os.path.exists(des_path_false):
            with open(des_path_false, 'r') as f:
                lines = f.readlines()
                count_false = len(lines)

        count_true = 0
        des_path_true = os.path.join(base_path, str(today), v+'.true')
        if os.path.exists(des_path_true):
            with open(des_path_true, 'r') as f:
                lines = f.readlines()
                count_true = len(lines)

        tmp_msg = '<p>' + k + '：非重复简历数（%s），重复简历数（%s）</p>'
        tmp_msg = tmp_msg % (count_false, count_true)
        msg += tmp_msg

    return msg



def main():
    '''统计前一天的重复简历数，并发送通知邮件。'''

    # 先从日志文件过滤需要的信息
    for k in log_file_dict:
        log_filter(k)

    # 生成邮件正文
    msg = get_email_msg()

    # 发送邮件
    title = '简历抓取-重复简历统计'
    common.sendEmail(title=title, message=msg)

if __name__ == '__main__':
    main()