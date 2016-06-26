# encoding: utf-8

import json
import MySQLdb
from extract_seg_insert import ExtractSegInsert
import re
# import redispipe
import datetime
import random
import traceback
import requests
import sys, logging
import common
reload(sys)
sys.setdefaultencoding('utf8')


class Vdict(dict):
    def __missing__(self, key):
        value = ''
        return value


class OldMysql(object):
    """将传入的json 入到MySQL"""
    def __init__(self, source, json_dict, job_category='', source_id=''):
        # with open(json_dict) as f:
        #     self.json_dict = json.load(f)
        # self.job_detail = self.json_dict
        #
        self.json_source = source
        if len(source_id) > 0:
            json_dict['id'] = source_id
            if source == 'cjol' and not source_id.startswith('J'):
                json_dict['id'] = 'J' + source_id
        self.job_detail = json_dict
        self.job_category = job_category
        # self.job_detail = self.json_dict['job_detail']
        # self.json_dict = json_dict
        # self.sql_config = {
        #         'host': "10.4.14.233",
        #         'user': "tuike",
        #         'passwd': "sv8VW6VhmxUZjTrU",
        #         'db': 'tuike',
        #         'charset': 'utf8'
        #     }
        self.sql_config = common.sql_config
        self.logger = common.log_init(__name__, 'oldmysql.log')
        self.logger.debug('hahahah')
        # self.sql_config = {
        #     'host': "localhost",
        #     'user': "root",
        #     # 'user': "testuser",
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
        job_de['name'] = job_detail.get('name')
        job_de['sex'] = job_detail.get('sex')
        job_de['marriage'] = None
        job_de['add_time'] = datetime.date.today().isoformat()
        marriage = job_detail.get('marital_status')
        if marriage == '已婚':
            job_de['marriage'] = 0
        elif marriage == '未婚':
            job_de['marriage'] = 1
        # job_de['working'] = 0   #todo job_detail['job_status']    ###########  等 sam 做处理
        # job_de['job_reason'] = None  # 51job 没有离职原因
        job_de['phone'] = job_detail.get('telephone')
        job_de['qq'] = None
        job_de['email'] = job_detail.get('email')
        try:
            if job_de['email'].endswith('qq.com'):
                tmp_str = job_de['email'][:job_de['email'].find('@')]
                num = re.compile('^[0-9]*$')
                if re.search(num, tmp_str):
                    job_de['qq'] = tmp_str
        except:
            pass
        job_de['birthday'] = job_detail.get('birthday')
        # job_de['ability'] = job_detail['name']   # 擅长领域 特长 貌似是自行输入的
        job_de['company_name'] = None
        work_experience_latest = job_detail.get('work_experience')
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
            self.logger.info('no company name')
        # job_de['job_reason'] = job_de.get('company_name')
        job_de['job'] = None
        try:
            job_de['job'] = work_experience_latest[0]['job_name']
        except:
            self.logger.info('no job name')
        job_de['position'] = job_detail.get('domicile')
        job_de['job_period'] = None
        try:
            job_de['job_period'] = work_experience_latest[0]['work_time']
        except:
            self.logger.info('no job_period')
        try:
            job_de['salary'] = work_experience_latest[0]['work_salary']
        except:
            job_de['salary'] = None
        job_de['project'] = None
        project = job_detail.get('project')
        try:
            job_de['project'] = project[0]['project_name']
        except:
            self.logger.info('no project name')
        # job_de['look_job'] = job_detail['name']  #
        job_de['expected_salary'] = job_detail.get('seged_expected_salary')
        job_de['expected_position'] = job_detail.get('expected_city')
        job_de['expected_job'] = job_detail.get('target_functions')
        job_de['school'] = None
        job_de['school'] = job_detail.get('school')
        job_de['degree'] = job_detail.get('degree')
        job_de['major'] = job_detail.get('major')
        if self.json_source == '51job':
            """51job 两反了"""
            tmp_major = job_de['major']
            job_de['major'] = job_de['school']
            job_de['school'] = tmp_major
        job_de['graduating_year'] = job_detail.get('graduate_time')
        job_de['isSearch'] = 0
        # 贤人馆 改成 3 区分开这些是从搜索库来的，并且没有联系方式
        job_de['isXrg'] = 3
        # 添加 push_status = 1 设置为可以推送状态
        job_de['push_status'] = 0   # 设为0 表示录入中
        # 将个人评价 保存在 MySQL 的 recommend_reason 中
        job_de['recommend_reason'] = job_detail.get('self_evaluation')
        # 设为现在推送  测试一下随机时间
        if type(self.job_category) is int:
            job_de['clickPushTime'] = datetime.datetime.now() - datetime.timedelta(minutes=random.choice(range(2,20)))
        job_de['recommend_reason'] = job_detail.get('self_evaluation')
        job_de['talent_mark'] = job_detail.get('id')
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
            self.logger.info('sql_str is {}'.format(sql_str))
        elif option == 'up':
            sql_r = ''
            for k in job_de:
                if job_de[k] is not None:
                    if k != 'talent_mark' and k != 'talent_source' and k != 'phone':
                        sql_r += "`" + str(k) + "`" + ' = ' + " '" + str(job_de[k]) + "', "
            if job_de['phone'] is None:
                job_de['phone'] = ' NULL '
            sql_str = 'update talent set ' + sql_r + " `phone` = " + job_de['phone'] +\
                      " where `talent_mark` = " + "'" + str(job_de['talent_mark']) +\
                      "'" + " and `talent_source`= " + "'" + str(job_de['talent_source']) + "'"

        return sql_str

    def parse_edu(self, job_detail):
        job_de = Vdict()
        job_de['']
        return  job_de

    def sql_edu(self, talent_id, job_de):
        num = 0
        for i in job_de['education']:
            edu_time = i['education_time']
            if edu_time.count('-') == 1:
                edu_time = edu_time.replace('-', '--')
            edu_time = edu_time.replace('.', '/')
            db = MySQLdb.connect(**self.sql_config)
            sql = """insert IGNORE  into talent_edu ( `talent_id`, `edu_no`,`edu_time`,`school_name`,`major`,`degree`,
`is_show`,`update_time`
) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')""".format(talent_id,num,edu_time,i['school'],
                                                             i['major'],i['degree'],1,datetime.datetime.now())
            cursor = db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            db.commit()
            num += 1
        pass

    def parse_work(self):
        pass

    def sql_work(self, talent_id, job_de):
        num = 0
        for i in job_de['work_experience']:
            db = MySQLdb.connect(**self.sql_config)
            work_time_after = i['work_time']
            if work_time_after.count('-') == 1:
                work_time_after = work_time_after.replace('-', '--')
            work_time_after = work_time_after.replace('.', '/')
            sql = """insert IGNORE into talent_work ( `talent_id`, `work_no`,`work_time`,`company_name`,`job`,
        `income`,`desc`,`update_time`
        ) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')""".format(talent_id, num, work_time_after,
                                                                     i.get('company_name'),
                                                                     i.get('job_name'), i.get('work_salary'), i.get('job_describe'),
                                                                     datetime.datetime.now())
            cursor = db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            db.commit()
            num += 1
        pass

    def parse_project(self):
        pass

    def sql_project(self, talent_id, job_de):
        num = 0
        #print job_de
        for i in job_de['project']:
            db = MySQLdb.connect(**self.sql_config)
            pro_time = i['project_time']
            if pro_time.count('-') == 1:
                pro_time = pro_time.replace('-', '--')
            pro_time = pro_time.replace('.', '/')
            sql = """insert IGNORE  into talent_project ( `talent_id`, `project_no`,`project_time`,`project_name`,
        `project_desc`, `is_show`,`update_time`
        ) VALUES ('{}','{}','{}','{}','{}','{}','{}')""".format(talent_id, num, pro_time,
                                                                     i.get('project_name'),
                                                                     i.get('project_describe'), 1,
                                                                     datetime.datetime.now())
            cursor = db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            db.commit()
            num += 1
        pass

    def find_talentid(self, source, mark, tofind):
        db = MySQLdb.connect(**self.sql_config)
        sql = """select {} from talent where talent_source = '{}' and talent_mark = '{}' """.format(tofind,
                                                                                                    source, mark)
        self.logger.info('sql is {}'.format(sql))
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        # print data
        if len(data) == 0:
            return None
        else:
            talent_id = data[0][0]
            self.logger.info('found talent id is {}'.format(talent_id))
            return talent_id

    def after_update(self, talent_id, auto_id):
        if type(self.job_category) is int:
            advisor_id = random.choice([66, 94, 65, 102, 90, 109, 97, 131, 133, 128, 113, 121, 137, 136, 111])
            sql = """update talent set `id` = '{}', `adviserid` = '{}', `job_category` = '{}' where
                auto_id = '{}'""".format(talent_id, advisor_id, self.job_category, auto_id)
        else:
            sql = """update talent set `id` = '{}' where
                auto_id = '{}'""".format(talent_id, auto_id)
        db = MySQLdb.connect(**self.sql_config)
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()
        return True


    def run_work(self):
        # r = redispipe.Rdsreport()
        user_res = self.search_user(self.json_source, self.job_detail['id'])
        db = MySQLdb.connect(**self.sql_config)
        job_de = self.parse_detal(self.job_detail)
        cur = db.cursor()

        if user_res == 3:
            self.logger.info(" do not need to do anything")
        elif user_res == 2:
            try:
                sql_res = self.sql_create('up')
                # print sql_res
                # print sql_up
                # b = cur.execute(sql_up)
                b = cur.execute(sql_res)
                if b == 1L:
                    self.logger.info('update success')
                db.commit()
            except Exception, e:
                logging.info('err msg is {}'.format(e), exc_info=True)
                self.logger.info('something wrong while updating MySQL')
                db.rollback()
        elif user_res == 1:
            try:
                sql_res = self.sql_create('in')
                self.logger.info('sql is {}'.format(sql_res))
                # print sql_in
                # b = cur.execute(sql_in)
                b = cur.execute(sql_res)
                if b == 1L:
                    self.logger.info('insert success')
                db.commit()
            except Exception, e:
                logging.info('err msg is {}'.format(e), exc_info=True)
                self.logger.info('something wrong while inserting MySQL')
                db.rollback()
        db.close()
        job_de2 = Vdict(self.job_detail)
        # 更新jobs 表的某些数据
        auto_id = self.find_talentid(self.json_source, job_de2['id'], 'auto_id')
        url = 'http://8082.tuikor.com/tkadmin/script/tid_jiami/' + str(auto_id)
        r = requests.get(url)
        talent_id = r.text
        try:
            # talent_id = self.find_talentid(job_de2['source'], job_de2['id'], 'id')
            self.after_update(talent_id, auto_id)
            try:
                self.sql_edu(talent_id, job_de2)
            except Exception, e:
                logging.info('err msg is {}'.format(e), exc_info=True)
                traceback.print_exc()
            try:
                self.sql_project(talent_id, job_de2)
            except Exception, e:
                logging.info('err msg is {}'.format(e), exc_info=True)
                traceback.print_exc()
            try:
                self.sql_work(talent_id, job_de2)
            except Exception, e:
                logging.info('err msg is {}'.format(e), exc_info=True)
                traceback.print_exc()
        except Exception, e:
            logging.info('err msg is {}'.format(e), exc_info=True)
            traceback.print_exc()


if __name__ == '__main__':
    o = OldMysql('51job', '303584215.json')
    o.run_work()

