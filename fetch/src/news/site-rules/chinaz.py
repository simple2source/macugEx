# coding: utf-8

from common import *
from bs4 import BeautifulSoup


def extract(html):
    pass


url = 'http://www.cnbeta.com/articles/478553.htm'
r = get_request(url)

r.encoding = 'utf-8'
with open('hu.html', 'w+') as f:
    f.write(r.text.encode('utf-8'))

soup = BeautifulSoup(r.text, 'html.parser')

article = soup.find('div', {'class': "newsTxtMainBar"})

title = article.find('h1', {'id': "YaHei"})
print title
content = article.find('div', {'class': 'content'})
print content
#
#
with open('hu2.html', 'w+') as f:
    f.write(unicode(article).encode('utf-8'))