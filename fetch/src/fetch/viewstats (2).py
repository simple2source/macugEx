# coding=utf-8

from fetchclass.showresult import *
from fetchclass.common import *
import sys

if __name__ == '__main__':
    para=''
    try:
        para=sys.argv[1]
    except:
        pass
    result_print(['cjol','51job','cjolsearch','51search','zhilian'],database_path)
    if para == 'mail':
        msg = result_email(['cjol','51job','cjolsearch','51search','zhilian'],database_path)
        sendEmail('default_main', '抓取数据报告', msg,msg_type=1)
        #print msg
        print 'sent Technich email'
    if para == 'pmail':
        msg = result_email(['cjol','51job','cjolsearch','51search','zhilian'],database_path)
        #print msg
        sendEmail('default_main', '抓取数据报告', msg,msg_type=1, des='P')
        print 'sent Product email'
