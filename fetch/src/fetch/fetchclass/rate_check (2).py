# coding:'utf-8'

from redispipe import *
import sys
from BaseFetch import BaseFetch
from common import *

r = Rdsreport()
       

if __name__ == '__main__':
    print('\n module_name list: cjolsearch, zhilian, 51job, 51search \n')
    # module_name = sys.argv[1]
    module_name = raw_input('input module_name :')
    class C_class(BaseFetch):
        def __init__(self, module_name):
            self.module_name = module_name
            self.db_root = db_root
            self.db_dir=os.path.join(self.db_root,self.module_name)
    c = C_class(module_name)
    print '\n save_dir: ', c.db_dir
    if module_name == 'cjolsearch':
        resume_pre = 'c_'
    elif module_name == 'zhilian':
        resume_pre = 'z_'
    elif module_name == '51job':
        resume_pre = 'wu_'
    elif module_name == '51search':
        resume_pre = 'wu_'
    while True:
        # print('input id:')
        resume_id = raw_input('input resume id: ')
        try:
            resume_id_after = resume_pre + str(resume_id)
            if r.check(resume_id_after):
                print r.test().get(resume_id_after)
                print('id exist in redis')
            else:
                print('id not exist in redis')
        except Exception, e:
            print('error, not in redis?', str(e))
        if c.resume_exist_chk(resume_id):
            print('id saved in db_dir')
        else:
            print('id not saved in db_dir')
        print('------------\n')

