# coding: utf-8

from common import *
from bs4 import BeautifulSoup


def extract(html):
    pass


url = 'http://36kr.com/p/5043791.html'
r = get_request(url)

r.encoding = 'utf-8'
with open('hu.html', 'w+') as f:
    f.write(r.text.encode('utf-8'))

soup = BeautifulSoup(r.text, 'html.parser')


article = soup.find('article', {'class': "single-post english-wrap"})

title = article.find('header', {'class': "single-post__title"})
content = article.find('section', {'class': 'article'})
print article
#
#
with open('hu2.html', 'w+') as f:
    f.write(unicode(article).encode('utf-8'))