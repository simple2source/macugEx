# -*- coding:utf-8 -*-

import sys
import requests
reload(sys)
sys.setdefaultencoding('utf8')
from bs4.element import Tag
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; '
                         'WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/28.0.1500.72 Safari/537.36'}


def fetch(link_url):
    tree = {}
    content_list = []
    resp = requests.get(link_url, headers=headers)
    data = resp.content
    print('content', data)
    soup = BeautifulSoup(data, "html5lib")
    elements = list(soup.select_one('#container').select_one('#content_left').children)
    f = open('search.txt', 'wb+')
    i = 0
    for ele in elements:
        try:
            print('ele bs4 type', type(ele))
            if isinstance(ele, Tag):
                i += 1
                title = ele.select_one('h3').text
                print('!!! title', title)
                contents = ele.select('div')
                c = ''
                for content in set(contents[1:]):
                    if content.text:
                        if content.text not in content_list:
                            c += content.text + '||'
                        content_list.append(content.text)
                f.write(str(i) + '、标题: ' + title + '\n')
                f.write('内容: ' + c + '\n')
                tree[i] = (title, c)
        except Exception as e:
            print('error:', e)
    f.close()
    print('tree: ', len(tree), tree)


if __name__ == '__main__':
    word = raw_input("请输入搜索关键字: ")
    url = 'https://www.baidu.com/s?wd={}&pn=40' \
          '&oq=%E5%BC%A0%E5%AE%B6%E7%95%8C%E6%97%85%E6%B8%B8&ie=utf-8&usm=5' \
          '&rsv_idx=1&rsv_pq=eebc302900002549&' \
          'rsv_t=40a6PvzHALnSzIgNz8N1UrQlmLG0UnuNKhz3kU%2BHlcia3FyVT89AI1C2AmI'.format(word)
    fetch(url)
