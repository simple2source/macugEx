# encoding: utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')
from bs4 import BeautifulSoup
import MySQLdb
import common
import lxml.html
from readability.readability import Document
import re
import MySQLdb.cursors

def no_img2(text):
    try:
        if text.find('<img') < 0:
            return True
        else:
            return False
    except Exception, e:
        print e
        return False

def no_img(text):  # True 代表没有图片
    p = re.compile('<img.+>')
    aa = re.search(p, text)
    if aa:
        # print aa.group()
        return False
    else:
        return True


def short_article(text, text_num=200):  # True 代表短文章
    # soup = BeautifulSoup(text, 'html.parser')
    try:
        # raw_text = soup.text
        raw_text = lxml.html.document_fromstring(text).text_content()
        if len(raw_text) < text_num:
            # print soup, 2222222222000000000000000022222222222,
            # print text
            # print raw_text
            return True
        else:
            return False
    except Exception, e:
        print e, 9999999999999999999999999
        return False

def comb(text, num):  # true 代表 短文章且没图， False 代表长文章，或者有图
    if no_img(text):
        if short_article(text, num):
            return True
        else:
            return False
    else:
        return False

def run1():
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor(MySQLdb.cursors.SSCursor)
    sql_1 = """select id, url, content from news """
    cursor.execute(sql_1)
    print cursor.rowcount
    i = 0
    row = True
    row = cursor.fetchone()

    while row is not None:
        i += 1
        if i % 100 == 0:
            print i, 666666666666666
        row = cursor.fetchmany(size=500)
        # print row
        for row_id, url, content in row:
        # print row_id
            if comb(content, 250) and 'v2ex.com' not in url:
                # print content, 111111111111111111111
                r = common.get_request(url)
                if r.url.startswith('http://mp.weixin.qq.com/'):
                    soup2 = BeautifulSoup(r.text, 'html.parser')
                    title = soup2.find('title').get_text().encode('utf8')
                    content = soup2.find('div', {'class': 'rich_media_content'})
                    content = unicode(content).encode('utf8')
                else:
                    content = Document(r.text.encode(r.encoding, 'ignore')).summary().encode('utf-8')
                    title = Document(r.text.encode(r.encoding)).short_title().encode('utf-8')
                db2 = MySQLdb.connect(**common.sql_config)
                cursor2 = db2.cursor()
                if not comb(content, 250) and 'mp.weixin.qq.com' in url:
                    sql = """update news set rating = 0, content = '{}' where id = '{}'""".format(db2.escape_string(content), row_id)
                    print 2222222222
                else:
                    sql = """update news set rating = -1, content = '{}' where id = '{}' """.format(db2.escape_string(content), row_id)
                try:
                    cursor2.execute(sql)
                    db2.commit()
                except Exception, e:
                    print e
                    db2.rollback()
                db.ping(True)
                db2.close()
                print row_id, 777777777777777777777
                print url
        # cursor.close()
    db.close()

def run():
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor(MySQLdb.cursors.SSCursor)
    sql_1 = """select id, url, content from news """
    cursor.execute(sql_1)
    print cursor.rowcount
    i = 0
    row = True
    row = cursor.fetchone()
    while row is not None:
        i += 1
        if i % 100 == 0:
            print i, 666666666666666
        row = cursor.fetchmany(size=500)
        # print row
        for row_id, url, content in row:
        # print row_id
            db2 = MySQLdb.connect(**common.sql_config)
            cursor2 = db2.cursor()
            if comb(content, 250) and 'v2ex.com' not in url and 'mp.weixin.qq.com' not in url:
                sql = """update news set rating = -1, content = '{}' where id = '{}' """.format(db2.escape_string(content), row_id)
                try:
                    cursor2.execute(sql)
                    db2.commit()
                except Exception, e:
                    print e
                    db2.rollback()
                db2.close()

def run3():
    db = MySQLdb.connect(**common.sql_config)
    cursor = db.cursor()
    n = 0
    sql_1 = """select id, url, content from news limit {}, 1000""".format(n)
    cursor.execute(sql_1)
    print cursor.rowcount
    i = 0
    row = cursor.fetchall()
    while len(row) > 0:
        i += 1
        if i % 100 == 0:
            print i, 666666666666666
        # row = cursor.fetchmany(size=500)
        # print row
        for row_id, url, content in row:
        # print row_id
            db2 = MySQLdb.connect(**common.sql_config)
            cursor2 = db2.cursor()
            if comb(content, 200) and 'v2ex.com' not in url and 'mp.weixin.qq.com' not in url :
                sql = """update news set rating = -1 where id = '{}' """.format(row_id)
                try:
                    print row_id, url
                    cursor2.execute(sql)
                    db2.commit()
                except Exception, e:
                    print e
                    db2.rollback()
                db2.close()
        db = MySQLdb.connect(**common.sql_config)
        cursor = db.cursor()
        n += 1000
        sql_1 = """select id, url, content from news limit {}, 1000""".format(n)
        cursor.execute(sql_1)
        row = cursor.fetchall()


if __name__ == '__main__':
    run3()
