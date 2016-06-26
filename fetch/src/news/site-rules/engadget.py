# coding: utf-8

from common import *
from bs4 import BeautifulSoup


def extract(html):
    pass


url = 'http://blog.jobbole.com/98200/'
r = get_request(url)

r.encoding = 'utf-8'
with open('hu.html', 'w+') as f:
    f.write(r.text.encode('utf-8'))

soup = BeautifulSoup(r.text, 'html.parser')

article = soup.find('div', {'class': "main-wrap tal"})

title = article.find('h1', {'class': "h1", "itemprop": "headline"})
content = article.find('div', {'class': 'copy post-body '})
print article
#
#
with open('hu2.html', 'w+') as f:
    f.write(unicode(article).encode('utf-8'))