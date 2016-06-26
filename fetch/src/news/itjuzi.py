# encoding: utf8
import common
import random
import json
from bs4 import BeautifulSoup
import requests
import os, copy

url_cm = 'https://www.itjuzi.com/company'
url_list = ['https://www.itjuzi.com/company',
            'https://www.itjuzi.com/person',
            'https://www.itjuzi.com/investfirm',
            'https://www.itjuzi.com/investor',
            'https://www.itjuzi.com/incubator',
            'https://www.itjuzi.com/tag',
            'http://www.itjuzi.com/company/foreign', ]
url_dict = {
    # 'company': {'url': 'http://www.itjuzi.com/company', 'tp': 1},
    'person': {'url': 'http://www.itjuzi.com/person', 'tp': 2},
    'investfirm': {'url': 'http://www.itjuzi.com/investfirm', 'tp': 4},
    'investor': {'url': 'http://www.itjuzi.com/investor', 'tp': 2},
    'incubator': {'url': 'http://www.itjuzi.com/incubator', 'tp': 1},
    'tag':  {'url': 'http://www.itjuzi.com/tag', 'tp': 3},
    'company_foreign': {'url': 'http://www.itjuzi.com/company/foreign', 'tp': 1}
}

url_dict2 = {
    'company': {'url': 'http://www.itjuzi.com/company', 'tp': 1},
}

headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':"www.itjuzi.com",
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}

s = requests.Session()
s.headers = headers

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    tag_soup = soup.find('ul', {'class': 'ui-filterui'})
    title_bar = soup.find('div', {'class': 'titlebar'}).get_text()
    tag_soup.find_all('li')
    d = Vividict()


def extract(text, tp):
    soup = BeautifulSoup(text, 'html.parser')
    if tp == 1:  # 公司
        tags_soup = soup.find_all('ul', class_='list-main-icnset')[1]
        tags_list = tags_soup.find_all('p', {'class': 'title'})
        keyword_list = [i.a.span.get_text().strip() for i in tags_list]
    elif tp == 2:  # 人类
        tags_soup = soup.find_all('b', class_='title')
        keyword_list = [i.a.get_text().strip() for i in tags_soup]
    elif tp == 3:  # 标签
        tags_soup = soup.find_all('ul', class_='list-main-normal')[1]
        tags_list = tags_soup.find_all('li')
        keyword_list = [i.a.get_text().strip().split(' ')[0] for i in tags_list]
    else:  # 投资
        tags_soup = soup.find_all('ul', class_='list-main-investset')[1]
        tags_list = tags_soup.find_all('p', {'class': 'title'})
        keyword_list = [i.a.span.get_text().strip() for i in tags_list]
    return keyword_list


def page_next(text):
    if text.find(u'下一页 →') > 0:
        return True
    else:
        return False


def run(url, tp):
    aa = common.get_request(url, timeout=8)
    url2 = url
    page = 1
    flag = True
    keyword_all = []
    while flag:
        print url
        keyword_list = extract(aa.text, tp)
        print keyword_list
        print '---------------'
        keyword_all.extend(keyword_list)
        print keyword_all
        if aa.text.find(u'下一页') < 0:
            flag = False
        else:
            page += 1
            headers['refer'] = url
            url = url2 + "?page={}".format(page)
            print url
            aa = common.get_request(url, headers=headers, timeout=8)
        common.rand_sleep(9, 4)
    return keyword_all



def run_company(url, tp):   # 针对桔子对公司的爬取限制，另外写的
    url2 = url
    page = 10
    flag = True
    keyword_all = []
    l_list = range(2, 2427)
    l_list2 = copy.copy(l_list)
    for i in l_list2:
        store_path1 = os.path.join(common.root_path, 'juzi', str(i)+'.html')
        if os.path.isfile(store_path1):
            l_list.remove(i)
        else:
            print store_path1
    print len(l_list), 999999999
    print l_list
    aa = common.get_request(url, timeout=18)
    headers2 = {'Origin': 'http://www.itjuzi.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
    ,'Accept': '*/*'
    ,'Referer': 'http://www.itjuzi.com/company?page=2410'
    ,'Cookie': 'grwng_uid=2e824b08-70ef-41f7-a9c8-62ff25d8f920; AWSELB=258D9D590E00B3DE939BD2301A2166BB8314D5BFDDA88D29F0E3F22E0935E83EF1C408A6B613204775BA26EA9BE8555ABB5A13289EDD9FCE01B44987A799A50A15E49578ED9A0D7D28BE3696012F59FED65EA97193'
    ,'Connection': 'keep-alive'}
    url_p = 'https://api.growingio.com/v2/eee5a46c52000d401f969f4535bdaa78/web/pv?stm=1459928218615'
    while flag:
        print url
        keyword_list = extract(aa.text, tp)
        print keyword_list
        print '---------------'
        keyword_all.extend(keyword_list)
        print keyword_all
        headers['refer'] = url
        url = url2 + "?page={}".format(page)
        print url
        headers2['refer'] = url
        aa = common.get_request(url, timeout=18)
        # bb = common.post_request(url_p, headers=headers2, data='6\x86\xf0D\x08`\x96`\\`S$\x15\x82\x01`\x1b\x01\x8d\x90&\x002\x10\x09\x9a\xf8\x08\xc0\x19\x80\x9c\x19QZ\xc8\x0c\xcc\x80FDA\x00\xec\x00q\x80\r$\x00np\xc3\xe0\x07H\xd7\x80\x96"\x03\xa8!\x90 +\x88\xeeX+w\xcb\x8b.\x00\xb4dru\xd6\x84\xd1]\x11\x91`\x8b\xa7\x91\n\x17\xf0\xf5\xcd\xca\xbf0\x01\x9dUc)\xd7\'df\xdchDd\xc6\xa4\x8c\xba\xdc\x08&\xba\x92\x08DATT\xf8\xc8\xf8R`\x00."\x82\xeeY\x02\x19\x00\xb6pd\x0cI\xce\xb8d\xdc\xc8<\x02\xee\x00\x16p\x9c\x8c\x18\xb5\x00\xeeph%\x02D"\xad}bP\x19\x00VJ\x00^PbX\x00\xf6E\x02\x00\x0e"\x00\xf4\xd3\x05s\x10\x00v\x00\x9en\x00N\x14"u\x19\x19s\xb0\x8b\x8b}\xad\x03\xc3c\x13+\xcb3k[\x00\xfck\x00\xe6\x08\x00\xbc\xb8\x9dhn\x006"Q\x9dWE\x87Y\xb8\x00\x8e"7\xa7\xdb\xe6G\xc1\x80\x00\xbe|p\n\x9e\x06\xa0\xd1ht\xfaC\x18X.d\xb3Yl\xf6T\x93\x85\xc6\xe4\xf1\xa3\xbc\xbe\x7f X*\x113\xe0"Q\x18\x9cA&\x82H\xa4\xd2n\x0c\x80>\x08\x01\xb4T\x00\x7f*\x01\xd0\x95\x00\x16\x11\x80W\x0c\x80\x01\x00\x07\xc2P\x04\x90\x00\xaa\x00T-\x00\n\xda\xdc\xa8D\x1d\xed\xca*\xc0J\xc82\xb7\x02\xa5Q\xa9\x80\xe6Yx!\xd8\xe6\xe1\xeb\xc0.W\x11\xb8\xd2c3p-\xe0\xf7U\x86\xdb`#\xd8\x1c\x8e\'3\xad\xb0om\xb8\xcc\xdd\x8fM\x8b\xc3S\x09\xf8C\xd5\xef/\xa7^\x10\x88\x02\xe9\x00')
        # print bb.content
        common.get_request('http://www.itjuzi.com/company/{}'.format(random.choice(range(1, 500))), timeout=10)
        store_path = os.path.join(common.root_path, 'juzi', str(page)+'.html')
        with open(store_path, 'w+') as f:
            f.write(aa.text.encode('utf8'))
        common.rand_sleep(30, 15)
        if len(l_list) == 0:
            flag = False
        else:
            page = random.choice(l_list)
            l_list.remove(page)
    return keyword_all

def name(url):
    a = url.split('//')[1]
    b = a.split('/')[1:]
    c = '_'.join(b)
    return c


if __name__ == '__main__':
    d = Vividict()
    for i in url_dict:
        try:
            d[i] = run(url_dict[i]['url'], url_dict[i]['tp'])
            print d
        except Exception, e:
            print i
            print e
        with open('tag_keyword.json', 'w+') as f:
            json.dump(d, f)

