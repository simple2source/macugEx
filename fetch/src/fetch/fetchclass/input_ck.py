#!/usr/bin/env python
# encoding: utf-8
"""
script to input cookie string to redis
auto deal with the redis hash type
"""
import MySQLdb
import os, random
import sys, redis
import liblogin
import requests
from bs4 import BeautifulSoup
import libaccount

def p_key(source):
    pre_key = ''
    if '51' in source:
        pre_key = 'cookie51_'
    elif 'cjol' in source:
        pre_key = 'cookiecjol_'
    elif 'zhilian' in source:
        pre_key = 'cookiezl_'
    else:
        print 'no valid source'
    return pre_key

if __name__ == '__main__':
    source = raw_input('please input your source:\n')
    a = libaccount.Manage(source=source, option='down')
    while 1:
        username = raw_input('input username:\n')
        ck_str = raw_input('input cookie string:\n')
        print ck_str
        print type(ck_str)
        if len(ck_str) > 0:
            # username = p_key(source) + username
            a.redis_ck_set(username, ck_str)
        else:
            print 'ck_str not right, please retry'
        print '\n' * 2

