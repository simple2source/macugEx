# encoding:utf8
import oldmysql
import common
import MySQLdb
import requests, json


class BTalent():
    def __init__(self, source, id_num, phone_num, name, email, seged_dict):
        self.json_source = source
        self.id_num = id_num
        self.sql_config = common.sql_config
        self.phone_num = phone_num
        self.name = name
        self.email = email
        self.seged_dict = seged_dict
        self.logger = common.log_init(__name__, 'buy2talent.log')


    def get_dict(self):
        """由简历id 搜索搜索库"""
        try:
            if self.json_source == 'cjol':
                id_num = 'J' + str(self.id_num)
            else:
                id_num = str(self.id_num)
            url = 'http://183.131.144.102:8090/supin_resume_v1/doc_v1/_search?q=id:{}&pretty=true'.format(id_num)
            res = requests.get(url)
            r_json = res.json()
            self.logger.info('res from es is {}'.format(res.json()))
            r_source = r_json["hits"]["hits"][0]
            return r_source
        except Exception as e:
            self.logger.error('get j_dict error', exc_info=True)


    def phone_sel(self):  # 看是否 unique key 冲突
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
            sql = """select phone, `id`, talent_mark, talent_source from talent where phone = '{}'""".format(self.phone_num)
            cursor.execute(sql)
            data = cursor.fetchall()
            if len(data) > 0:
                phone, t_id, s_id, source = data[0]
                return phone, t_id, s_id, source  # 有这个phone 的存在于 talent
            else:
                return None
        except Exception as e:
            self.logger.error('select phone error', exc_info=True)
            return None

    def mark_sel(self):  # 看之前是否 该talentmark已经有 phone，不管有没有都将其保存在 contact_info 字段
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
            if self.json_source == 'cjol':
                id_num = 'J' + str(self.id_num)
            else:
                id_num = str(self.id_num)
            sql = """select phone, id from talent where talent_mark = '{}' and talent_source = '{}'""".format(id_num, self.json_source)
            cursor.execute(sql)
            data = cursor.fetchall()
            self.logger.info('data is {}'.format(data))
            phone = data[0][0]
            talent_id = data[0][1]
            if phone is None:
                self.logger.error('find talent_mark and talent_source but no phone number')
                return 1
            else:
                return talent_id
        except Exception as e:
            self.logger.error('select phone error', exc_info=True)
            return None

    def phone_up(self):
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
            if self.json_source == 'cjol':
                id_num = 'J' + str(self.id_num)
            else:
                id_num = str(self.id_num)
            if self.mark_sel() == 1:
                sql = """update talent set phone = '{}', email = '{}', `name` = '{}' where talent_mark = '{}'
            and talent_source = '{}'""".format(self.phone_num, self.email, self.name, id_num, self.json_source)
            # else:
            #     import json
            #     json_str = json.dumps({'phone': self.phone_num, 'email': self.email, 'name': self.name})
            #     sql = """update talent set contact_info = '{}' where talent_mark = '{}'
            # and talent_source = '{}'""".format(json_str, id_num, self.json_source)
                self.logger.info('sql is {}'.format(sql))
                res = cursor.execute(sql)
                db.commit()
                db.close()
                if res == 1L:
                    self.logger.info('update phone success')
                    return 1
                else:
                    self.logger.error('update phone fail')
                    return 2
            else:
                return 3   # 后面把返回的json 直接存于 contact info 字段
        except Exception as e:
            self.logger.error('update phone error', exc_info=True)
            return None

    def contant_up(self, json_str, adviser_id):
        """将返回的json 保存在 contact info 字段"""
        try:
            db = MySQLdb.connect(**self.sql_config)
            cursor = db.cursor()
            if self.json_source == 'cjol':
                id_num = 'J' + str(self.id_num)
            else:
                id_num = str(self.id_num)
            sql = """update talent set contact_info = '{}' where talent_mark = '{}'
        and talent_source = '{}'""".format(json.dumps(json_str), id_num, self.json_source)
            self.logger.info('sql is {}'.format(sql))
            res = cursor.execute(sql)
            db.commit()
            # 顺手更新一下 adviserId
            if len(str(adviser_id)) > 0 and adviser_id is not None:
                sql_adviser = """update talent set adviserId = '{}' where talent_mark = '{}'
            and talent_source = '{}' and adviserId is NUll""".format(adviser_id, id_num, self.json_source)
                res2 = cursor.execute(sql_adviser)
                db.commit()
                db.close()
                if res2 == 1L:
                    self.logger.info('set adviser id success')
                else:
                    self.logger.info('do not touch adviser id')
            if res == 1L:
                self.logger.info('update contact_info success')
                return 1
            else:
                self.logger.error('update contact_info fail')
                return 2
        except Exception as e:
            self.logger.error('update phone error', exc_info=True)
            return None


    def main(self):
        """先搜索库插入大talent表，然后搜索电话号码"""
        # r_json = self.get_dict()  # 直接用解析的结果
        r_json = self.seged_dict
        self.logger.info('r json is {}'.format(r_json))
        # if len(r_json) > 0:
        try:
            # res = r_json['_source']
            res = r_json
            # source = res['source']
            app = oldmysql.OldMysql(self.json_source, res, source_id=self.id_num)
            app.run_work()  # 插入到talent 表
            res1 = self.phone_sel()
            if res1 is None:  # 本来talent 没有这个电话号码
                self.logger.info('cannot find this phone in talent', exc_info=True)
                aa = self.phone_up()
                if aa == 1:
                    self.logger.info('update phone success')
                    return -1
                elif aa == 2:
                    self.logger.error('update phone fail')
                    return -2
                elif aa == 3:
                    self.logger.info('this source id already has phone')
                    return -3
                else:
                    self.logger.info('phone operate error')
                    return -4
            else:
                phone, t_id, s_id, source = res1
                self.logger.info('alreadly has this phone {}, talent_id {}, sourceid {}, source {}'.format(
                    phone, t_id, s_id, source
                ))
                return t_id
        except Exception as e:
            # print 'Cannot find this id in es'
            self.logger.critical('error, seg this resume error', exc_info=True)
            return -5

