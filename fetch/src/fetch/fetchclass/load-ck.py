# coding: utf8
""" use once , read cookie txt and pass it to redis
    sync cookie txt file and redis hash key
"""

import os
import urlparse
import libaccount

cookie_dir = '/data/spider/cookie'

for root, path, files in os.walk(cookie_dir):
    # print root, path, files, 99988888
    cookie_file_list = files
cookie_file_list= [n for n in cookie_file_list if n.endswith('.txt')]
cookie_51 = [n for n in cookie_file_list if n.startswith('51_')]
# print cookie_51
cookie_cjol = [n for n in cookie_file_list if n.startswith('cjol') ]
cookie_zl = [n for n in cookie_file_list if n not in cookie_51 if n not in cookie_cjol]

for c_51 in cookie_51:
    fpath = os.path.join(cookie_dir, c_51)
    # print fpath, 9999999999
    with open(fpath) as f:
        ff = f.read()
    # print ff
    ck_dict = urlparse.parse_qs(ff)
    # print ck_dict
    if ck_dict.keys().count('UserName') == 1:
        username=ck_dict['UserName'][0]
        a = libaccount.Manage(source='51job')
        a.redis_ck_set(username, ff)

for c_cjol in cookie_cjol:
    fpath = os.path.join(cookie_dir, c_cjol)
    # print fpath
    with open(fpath) as f:
        ff = f.read()
    ck_dict = urlparse.parse_qs(ff)
    if ck_dict.keys().count(' CompanyID') == 1:
        company_id = ck_dict[' CompanyID'][0]
        if str(company_id) == '317080':
            username = 'LHYS'
        if str(company_id) == '308380':
            username = 'qimingguanggao'
        a = libaccount.Manage(source='cjol')
        a.redis_ck_set(username, ff)

for c_z in cookie_zl:
    fpath = os.path.join(cookie_dir, c_z)
    # print fpath
    with open(fpath) as f:
        ff = f.read()
    username = os.path.splitext(c_z)[0]
    a = libaccount.Manage(source='zhilian')
    a.redis_ck_set(username, ff)