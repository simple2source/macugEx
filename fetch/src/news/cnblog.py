# encoding: utf8

import common
from bs4 import BeautifulSoup
import time
import re, logging, json
from readability.readability import Document
import os, sys
reload(sys)
sys.setdefaultencoding('utf8')

# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'cnblog.log')
logging.config.dictConfig(log_dict)
logging.info('hahahahha, start rss')
sql_config = common.sql_config


def all_blog():
    url_cnblog = 'http://www.cnblogs.com/AllBloggers.aspx'
    aa = common.get_request(url_cnblog)
    soup_a = BeautifulSoup(aa.text, 'html.parser')
    aa = soup_a.find_all('td')
    aa = aa[1:]
    a_dict = dict()
    for i in aa:
        blog_url = i.a.get('href')
        blog_name = blog_url[blog_url.find('com/') + 4:-1]
        blog_cnname = i.a.get_text().strip()
        a_dict.update({blog_name: blog_cnname})
    return a_dict

def blog_info(text):
    p1 = re.compile(r'cb_blogId=\d+')
    p3 = re.compile(r'cb_entryId=\d+')
    p2 = re.compile(r"currentBlogApp = '\S+")
    blog_id, blog_app, post_id = None, None, None
    try:
        blog_id = re.search(p1, text).group().split('=')[1]
        post_id = re.search(p3, text).group().split('=')[1]
        blog_app = re.search(p2, text).group().split(' = ')[1].split("'")[1]
        # time_cc = ''.join(time.time().split('.'))
    except:
        pass
    # print blog_id, blog_app, post_id
    return blog_id, blog_app, post_id

def kword(blog_id, blog_app, post_id):
    par = {'blogApp': blog_app,
     'blogId': blog_id,
     'postId': post_id}
    url = 'http://www.cnblogs.com/mvc/blog/CategoriesTags.aspx'
    keyword = ''
    try:
        ab = common.get_request(url, params=par)
        result = ab.json()
        tag = result['Tags']
        tag = tag[tag.find(':')+2:]
        cate = result['Categories']
        cate = cate[cate.find(':')+2:]
        so1 = ''
        so2 = ''
        try:
            so1 = BeautifulSoup(tag, 'html.parser').get_text()
        except:
            pass
        try:
            so2 = BeautifulSoup(cate, 'html.parser').get_text()
        except:
            pass
        keyword = so1 + ',' + so2
        # print keyword, 999999999999999999999
    except:
        pass
    return keyword


def extract(text):
    soup = BeautifulSoup(text, 'html.parser') # , from_encoding="utf8")
    aaa = soup.find('li', {'id': 'EntryTag'})
    print aaa
    bbb = soup.find('div', {'id': 'BlogPostCategory'})
    tag_str = ''
    print bbb
    soup1 = soup.find('div', {'id': 'cnblogs_post_body'})
    if soup1:
        try:
            content = str(soup1)
            logging.info('find content in html tag')
        except:
            content = Document(text).summary()
            logging.info('conver soup to string error so via readability', exc_info=True)
    else:
        content = Document(text).summary()
        logging.info('find content via readability')
    try:
        aaaa = aaa.find_all('a')
        tag_list = [i2.get_text for i2 in aaaa]
        tag_str = ','.join(tag_list)
        aaab = bbb.find_all('a')
        tag_list2 = [i2.get_text for i2 in aaab]
        tag_str += ','.join(tag_list2)
    except Exception, e:
        # print Exception, e
        logging.error('cant find keyword in html', exc_info=True)
    return tag_str, content

def main(blog_name):
    sql_name = 'cnblog_' + blog_name
    page = 1
    flag = True
    url_0 = "http://www.cnblogs.com/{}/".format(blog_name)
    url_1 = "http://www.cnblogs.com/{}/".format(blog_name)
    while flag:
        print url_1
        try:
            bb = common.get_request(url_1)
            logging.info('return url {} success '.format(bb.url))
            print bb.url
            soup_2 = BeautifulSoup(bb.text, 'html.parser')
            with open('asdf.html', 'w+') as f:
                f.write(bb.text.encode('utf8'))
            b2 = soup_2.find_all('a', {'id': re.compile('homepage1_\S+_TitleUrl_\S+?')})  # 某页的文章链接
            for i_text in b2:
                article_url = i_text.get('href')
                print article_url
                logging.info('article is {}'.format(article_url))
                article_title = i_text.get_text().strip()
                if not common.select(article_url, blog_name):
                    article = common.get_request(article_url)
                    pub_time = common.re_time(article.text)
                    keyword, content = extract(article.text)
                    blog_id, blog_app, post_id = blog_info(article.text)
                    keyword = kword(blog_id, blog_app, post_id)
                    common.sql_insert(sql_name, article_url, article_title, content, pub_time, keyword)
                    common.rand_sleep(6, 1)
            page += 1
            re_str = url_0 + r'default\S+page={}'.format(page)
            print re_str
            pp = re.compile(re_str)
            ppp = re.search(pp, bb.text)
            if ppp is None:
                flag = False
            else:
                url_1 = ppp.group()
            common.rand_sleep(7, 1)
        except Exception, e:
            print Exception, e
            logging.error('run error', exc_info=True)


if __name__ == '__main__':
    blog_list = all_blog()
    for i in blog_list:
        main(i)

