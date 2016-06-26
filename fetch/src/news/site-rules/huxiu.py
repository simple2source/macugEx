# coding: utf-8

from common import *
from bs4 import BeautifulSoup


def extract(html):
    pass


url = 'http://www.huxiu.com/article/140140/1.html?f=wangzhan'
r = get_request(url)

r.encoding = 'utf-8'
with open('hu.html', 'w+') as f:
    f.write(r.text.encode('utf-8'))

soup = BeautifulSoup(r.text, 'html.parser')


article = soup.find('div', {'class': "article-wrap"})

title = article.find('h1', {'class': "t-h1"})
content = article.find('div', {'id': 'article_content'})
print article


with open('hu2.html', 'w+') as f:
    f.write(unicode(article).encode('utf-8'))

