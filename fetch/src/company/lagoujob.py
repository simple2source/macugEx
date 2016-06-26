# coding: utf-8

import common
import lgtransfer2
import sqlite3

db = sqlite3.connect('lagou.db')

cur = db.cursor()
cur.execute('select company_id from lagou')
data = cur.fetchall()
# print data
# print len(data)
for i in data:
    company_id = i[0]
    print company_id
    url = 'http://www.lagou.com/gongsi/{}.html'.format(i)
    lgtransfer2.run_work(url)
