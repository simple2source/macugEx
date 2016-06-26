# encoding: utf8

import requests
import json
import MySQLdb, sys, time
reload(sys)
sys.setdefaultencoding('utf8')

sql_config = {
    'host': "localhost",
    'user': "testuser",
    'passwd': "",
    'db': 'tuike',
    'charset': 'utf8',
}
# sql_config = {
#     'host': "10.4.14.233",
#     'user': "tuike",
#     'passwd': "sv8VW6VhmxUZjTrU",
#     'db': 'tuike',
#     'charset': 'utf8',
# }

s = requests.Session()

headers = {
        'Host': 'open.taou.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.0.2; MI 2 MIUI/V7.1.5.0.LXACNCK)/{Xiaomi MI 2}  [Android 5.0.2/21]/MaiMai 4.5.8(1135)',
        'Origin': 'https://maimai.cn',
        'Accept': '*/*',
        'Referer': 'https://maimai.cn/contact/dist2_list?count=14261',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'X-Requested-With': 'com.taou.maimai',
        }

# GET /maimai/contact/v3/feed?page=1&u=259592&access_token=2.00IOgcnBc9xsMBf9c9031477sUNAQC&version=4.5.8&_csrf=ErP9OU5H-_ruMV2rxprThRb5as8zvBl8D-dU&channel=XiaoMi&dist=2

# token list  每页10个
data1 = {   # 能翻100多页
        'page':	1,
        'u': 259592,
        'access_token':	'2.00IOgcnBc9xsMBf9c9031477sUNAQC',
        'version': '4.5.8',
        '_csrf': 'ErP9OU5H-_ruMV2rxprThRb5as8zvBl8D-dU',
        'channel': 'XiaoMi',
        'dist':	2,
        }
data2 = {  # 能翻200多页
        'page':	1,
        'u': 409070,
        'access_token':	'3339ae2348c3ffeb68e5837b40a1a586',
        'version': '4.5.8',
        '_csrf': 'tZls9Y8i-IaQtaA505jHAdeKu4U45YkoqOZI',
        'channel': 'XiaoMi',
        'dist':	2,
        }
data3 = {  # 能翻600多页
        'page':	1,
        'u': 248018,
        'access_token':	'bb268f0ab9c7103c798807ae00cdf317',
        'version': '4.5.8',
        '_csrf': 'ONdfRnx0-n_ZKRgoiQnFcnZGYYFgF-o1Fk7A',
        'channel': 'XiaoMi',
        'dist':	2,
        }

data_list = [data1, data2, data3]

url = 'https://open.taou.com/maimai/contact/v3/feed?'

# r = s.get(url, headers=headers, params=data, verify=False)

# print r.text


def select(mm_id):
    sql = " select id from maimai where mm_id = '{}' ".format(mm_id)
    db = MySQLdb.connect(**sql_config)
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    print data
    db.close()
    try:
        if len(data) > 0:
            return True
        else:
            return False
    except Exception, e:
        print Exception, e
        return False


def main(data, page):
    data['page'] = page
    r = s.get(url, headers=headers, params=data, verify=False)
    r_json = r.json()
    return r_json

def sql_in(data,j_dict):
    sql = """insert into maimai ( `source`, """
    for i in j_dict:
        sql += "`{}`,".format(i)
    sql = sql[:-1]
    sql += ") values ( '{}', ".format(data)
    for i in j_dict:
        sql += "'{}',".format(str(j_dict[i]).replace("'", "''"))
    sql = sql[:-1]
    sql += ')'
    # print sql.encode('utf8')
    return sql

    # sql = """ insert into maimai (`source`,`industry`,`jobtype`,`cmf2`,`cmf1`,`rank`,`local_mobile`,`mm_id`,`dist`,
    # `utype`,`line3`,`line2`,`line1`,`in_app`,`lv`,`tid`,`status`,`company`,`pub`,`ouid`,`cmf`,`judge`,`name`,`career`,
    # `gender`)"""

def d_convert(j2_dict):
    #
    # print '-----------'
    # print j2_dict
    # print '__________'
    aaa = j2_dict.pop('line4', None)
    try:
        industry = aaa.split('|')[0]
    except:
        industry = ''
    try:
        jobtype = aaa.split('|')[1].split('，')[0]
    except:
        jobtype = ''

    j2_dict.pop('d1type', None)
    j2_dict.pop('oline2', None)
    j2_dict.pop('py', None)
    j2_dict.pop('id', None)
    mm_id = j2_dict.pop('mmid', None)
    j2_dict['industry'] = industry
    j2_dict['jobtype'] = jobtype
    j2_dict['mm_id'] = mm_id
    return j2_dict


def run(data, page):
    try:
        r_json = main(data, page)
        j_dict = r_json #json.loads(r_json)
        # print r_json
        j2_dict = j_dict['contacts']
        if data == data1:
            dd = '1'
        elif data == data2:
            dd = '2'
        elif data == data3:
            dd = '3'
        # print j2_dict
        if len(j2_dict) > 0:
            db = MySQLdb.connect(**sql_config)
            cursor = db.cursor()
            for i in j2_dict:
                j3_dict = d_convert(i)
                sqlin = sql_in(dd, j3_dict)
                if not select(j3_dict['mm_id']):
                    try:
                        cursor.execute(sqlin)
                        db.commit()
                    except:
                        print sqlin
                        return False
            db.close()
            return True
        else:
            return False
    except Exception, e:
        print Exception, e, 9999999999999
        return False


if __name__ == '__main__':
    while 1:
        page = 1
        for d in data_list:
            while 1:
                print 'NOW page is ', page, '+++++++++++++++++++++++++++++++++++++'
                aa = run(d, page)
                if not aa:
                    break
                page += 1
                time.sleep(2)
            print 'switching'
        print 'done'
        time.sleep(60*60*4)

