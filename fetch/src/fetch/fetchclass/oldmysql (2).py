# encoding: utf-8

import json
import MySQLdb
from extract_seg_insert import ExtractSegInsert
import re
import redispipe
import datetime


class Vdict(dict):
    def __missing__(self, key):
        value = ''
        return value


class OldMysql(object):
    """将传入的json 入到MySQL"""
    def __init__(self, source, json_dict):
        # with open(json_dict) as f:
        #     self.json_dict = json.load(f)
        # self.job_detail = self.json_dict
        #
        self.json_source = source
        self.job_detail = json_dict
        # self.job_detail = self.json_dict['job_detail']
        # self.json_dict = json_dict
        self.sql_config = {
                'host': "10.4.14.233",
                'user': "tuike",
                'passwd': "sv8VW6VhmxUZjTrU",
                'db': 'tuike',
                'charset': 'utf8'
            }
        # self.sql_config = {
        #     'host': "localhost",
        #     'user': "testuser",
        #     'passwd': "",
        #     'db': 'tuike',
        #     'charset': 'utf8',
        # }

    def search_user(self, source, id_num):
        """ 搜索是否在MySQL中
        """
        db = MySQLdb.connect(**self.sql_config)
        cur = db.cursor()
        sql = """select phone from talent WHERE talent_source = '{}' and talent_mark = '{}' """.format(source, id_num)
        res = cur.execute(sql)
        data = cur.fetchall()
        try:
            dd = data[0][0]
        except:
            dd = None
        if res == 0L:  # 没有记录，执行插入，
            return 1
        elif dd is None:  # 有记录，但是没有手机号码，更新
            return 2
        else: # 有记录，有手机号码， 不做处理
            return 3

    def parse_detal(self, job_detail):
        job_de = Vdict()
        try:
            job_de['name'] = job_detail['name']
        except:
            job_de['name'] = None
        job_de['sex'] = job_detail['sex']
        job_de['marriage'] = None
        job_de['add_time'] = datetime.date.today().isoformat()
        marriage = job_detail['marital_status']
        if marriage == '已婚':
            job_de['marriage'] = 0
        elif marriage == '未婚':
            job_de['marriage'] = 1
        # job_de['working'] = 0   #todo job_detail['job_status']    ###########  等 sam 做处理
        # job_de['job_reason'] = None  # 51job 没有离职原因
        try:
            job_de['phone'] = job_detail['telephone']
        except:
            job_de['phone'] = None
        job_de['qq'] = None
        try:
            job_de['email'] = job_detail['email']
        except:
            job_de['email'] = None
        try:
            if job_de['email'].endswith('qq.com'):
                tmp_str = job_de['email'][:job_de['email'].find('@')]
                num = re.compile('^[0-9]*$')
                if re.search(num, tmp_str):
                    job_de['qq'] = tmp_str
        except:
            pass
        job_de['birthday'] = job_detail['birthday']
        # job_de['ability'] = job_detail['name']   # 擅长领域 特长 貌似是自行输入的
        job_de['company_name'] = None
        try:
            work_experience_latest = job_detail['work_experience']
        except:
            work_experience_latest = None
        company_list = []
        try:
            for i in work_experience_latest:
                company_list.append(i['company_name'])
        except:
            pass
        job_de['companies'] = ' '.join(company_list)
        try:
            job_de['company_name'] = work_experience_latest[0]['company_name']
        except:
            print 'no company_name'
        job_de['job_reason'] = job_de['company_name']
        job_de['job'] = None
        try:
            job_de['job'] = work_experience_latest[0]['job_name']
        except:
            print 'no job_name'
        job_de['position'] = job_detail['domicile']
        job_de['job_period'] = None
        try:
            job_de['job_period'] = work_experience_latest[0]['work_time']
        except:
            print 'no job_period'
        try:
            job_de['salary'] = work_experience_latest[0]['work_salary']
        except:
            job_de['salary'] = None
        job_de['project'] = None
        project = job_detail['project']
        try:
            job_de['project'] = project[0]['project_name']
        except:
            print 'no project name'
        # job_de['look_job'] = job_detail['name']  #
        job_de['expected_salary'] = job_detail['seged_expected_salary']
        job_de['expected_position'] = job_detail['seged_expected_city']
        job_de['expected_job'] = job_detail['seged_target_functions']
        job_de['school'] = None
        job_de['school'] = job_detail['school']
        job_de['degree'] = job_detail['degree']
        job_de['major'] = job_detail['major']
        if self.json_source == '51job':
            """51job 两反了"""
            tmp_major = job_de['major']
            job_de['major'] = job_de['school']
            job_de['school'] = tmp_major
        job_de['graduating_year'] = job_detail['graduate_time']
        job_de['isSearch'] = 1
        job_de['talent_mark'] = job_detail['id']
        job_de['talent_source'] = self.json_source
        for k in job_de:
            """MySQL里面貌似没有为空的，有null"""
            if job_de[k] == '' or job_de[k] is None:
                job_de[k] = None
        return job_de

    def sql_create(self, option):
        job_de = self.parse_detal(self.job_detail)
        if option == 'in':
            sql_col = ''
            sql_value = ''
            for k in job_de:
                if job_de[k] is not None:
                    sql_col += k + ', '
                    sql_value += "'" + str(job_de[k]) + "', "
            sql_str = "insert into talent ( " + sql_col[:-2] + " ) values( " + str(sql_value)[:-2] + " )"
        elif option == 'up':
            sql_r = ''
            for k in job_de:
                if job_de[k] is not None:
                    if k != 'talent_mark' and k != 'talent_source' and k != 'phone':
                        sql_r += "`" + str(k) + "`" + ' = ' + " '" + str(job_de[k]) + "', "
            if job_de['phone'] is None:
                job_de['phone'] = ' NULL '
            sql_str = 'update talent set ' + sql_r + " `phone` = " + job_de['phone'] +\
                      " where `talent_mark` = " + "'" + job_de['talent_mark'] +\
                      "'" + " and `talent_source`= " + "'" + str(job_de['talent_source']) + "'"

        return sql_str



    def run_work(self):
        r = redispipe.Rdsreport()
        user_res = self.search_user(self.json_source, self.job_detail['id'])
        db = MySQLdb.connect(**self.sql_config)
        job_de = self.parse_detal(self.job_detail)
        cur = db.cursor()

        if user_res == 3:
            print " do not need to do anything"
        elif user_res == 2:
            try:
                sql_res = self.sql_create('up')
                print sql_res
                # print sql_up
                # b = cur.execute(sql_up)
                b = cur.execute(sql_res)
                if b == 1L:
                    print 'update success'
                db.commit()
            except Exception, e:
                print Exception, str(e)
                print 'something wrong while updating MySQL'
                db.rollback()
        elif user_res == 1:
            try:
                sql_res = self.sql_create('in')
                print sql_res
                # print sql_in
                # b = cur.execute(sql_in)
                b = cur.execute(sql_res)
                if b == 1L:
                    print 'insert success'
                db.commit()
            except Exception, e:
                print Exception, str(e)
                print 'something wrong while inserting MySQL'
                db.rollback()
        db.close()


if __name__ == '__main__':
    o = OldMysql('51job', '303584215.json')
    o.run_work()

