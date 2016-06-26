# encoding: utf8

import common
from bs4 import BeautifulSoup
import time, re, logging, json, MySQLdb, os, sys
from readability.readability import Document
reload(sys)
sys.setdefaultencoding('utf8')

# init other log
with open(common.json_config_path) as f:
    ff = f.read()
logger = logging.getLogger(__name__)
log_dict = json.loads(ff)
log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'mux.log')
logging.config.dictConfig(log_dict)
logging.info('start fetching article from mux')
sql_config = common.sql_config

def get_content(text):
    soup = BeautifulSoup(text, 'html.parser')
    article = soup.find(class_='post')
    if article:
        try:
            content = str(article)
            logging.info('find content in html tag')
        except:
            content = Document(text).summary()
            logging.info('conver soup to string error so via readability', exc_info=True)
    else:
        content = Document(text).summary()
        logging.info('find content via readability')
    return content

def main():
    source = 'mux'
    page = 1
    flag = True
    url = 'http://mux.baidu.com/?page_id=10&paged={}'.format(page)
    while flag:
        try:
            print url
            res = common.get_request(url)
            logging.info('return url {} success'.format(res.url))
            print res.url
            soup = BeautifulSoup(res.text, 'html.parser')
            with open('temp.html', 'w+') as f:
                f.write(res.text.encode('utf8'))
            articles = soup.find_all('div', class_='artical_inner')
            for item in articles:
                contents = item.contents
                article_url = contents[9].a.get('href')
                article_title = str(contents[3].a.get('title')).strip()
                if not common.select(article_url, source):
                    pub_time = time.strftime('%Y-%m-%d',\
                        time.strptime(str(contents[5].get_text()).split('|')[-1].strip(), '%Y年%m月%d日'))
                    keyword = str(contents[5].get_text()).split('|')[-2].strip()
                    content = get_content(common.get_request(article_url).text);
                    print article_title
                    common.sql_insert(source, article_url, article_title, content, pub_time, keyword)
                    common.rand_sleep(6, 1)
            page += 1
            re_str = r'http://mux.baidu.com/\?page_id=10\S+paged={}'.format(page)
            pat = re.compile(re_str)
            s_r = re.search(pat, res.text)
            if s_r is None:
                flag = False
            else:
                url = 'http://mux.baidu.com/?page_id=10&paged={}'.format(page)
            common.rand_sleep(7, 1)
        except Exception, e:
            print Exception, e
            logging.error('run error', exc_info=True)

if __name__ == '__main__':
    main()