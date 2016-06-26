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

article = soup.find('div', {'class': "layoutleft"})

title = article.find('h3', {'id': "title"})
print title
content = article.find('div', {'class': 'bort'})
print content
#
#
with open('hu2.html', 'w+') as f:
    f.write(unicode(article).encode('utf-8'))