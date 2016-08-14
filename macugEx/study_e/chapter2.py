# -*- coding:utf-8 -*-
import math


# 斐波那契
def fibs(x):
    a = 1
    b = 0
    for _ in range(x):
        a, b = b, a + b
        print b
    return b

fibs(10)

print '-------'

# 斐波那契 递归实现


def fibs_recursion(y):
    if y <= 1:
        return y
    return fibs_recursion(y-1) + fibs_recursion(y-2)
print fibs_recursion(10)


# 字符串转化为 int http://stackoverflow.com/questions/24565966/convert-string-to-int-without-int


def transformation(m):
    # 此方法无法转化浮点型
    rtr = 0
    for c in m:
        rtr = rtr * 10 + ord(c) - ord('0')
    return rtr

print '*****'

# 另一种思路使用字典做映射实现


def str2int_dict(v):
    d = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
         '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '.': '.'}
    num = 0
    length = len(v) - 1
    if '.' in v:
        l1 = v.split('.')
        length = len(l1[0]) - 1
    for i in v:
        if i not in d.keys():
            raise ValueError("not a digital")
        if i == '.':
            length = -1
            continue
        num = d[i] * (10 ** length) + num
        length = length - 1
        print num
    print num
    print type(num)
str2int_dict('10246600.0062323435354')


print type(ac)
print type(ad)
if 1:
    print 'www'
