# -*- coding:utf-8 -*-

# a iter object
# 参考资料
# http://mp.weixin.qq.com/s?__biz=MzAxMjUyNDQ5OA==&mid=2653552192&idx=1&sn=47475d265c5360bf2ac23789dd5e7fe2&chksm=806dd0fdb71a59ebf035922bd58550c2989fc898f3e486b14b1c6ef9f0f4bcb2727e5d6e96d1&mpshare=1&scene=23&srcid=0710HtJtvVfM9JGBi7cva6we#rd
# http://codingpy.com/article/python-generator-notes-by-kissg/

import time
import queue


class Counter(object):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __iter__(self):
        # 必须实现__iter__方法,返回一个iterator
        # first step:
        #            for 会调用此方法
        print('i will iter')
        return self

    def next(self):
        # in py3, user __next__
        # 内置next function 会调用此方法
        # second step:
        #            for会通过实现next方法进行取值
        if self.start > self.stop:
            raise StopIteration
        self.start += 1
        return self.start - 1

c = Counter(3, 5)
for i in c:
    print(i)

# generator


def gen(num):
    print('will create a generator')
    for j in range(num):
        yield j
        print('j:after')
        yield 5

genra = gen(2)
print(dir(genra))
for k in genra:
    print('k gen:', k)


def countdown(n):
    print('countdown from {}'.format(n))
    while n > 0:
        new_value = yield n
        time.sleep(1)
        print('new_value', new_value)
        if new_value is not None:
            n = new_value
        else:
            n -= 1

cut = countdown(5)
for c in cut:
    print('c:', c)
    cut.send(None)
    # if c == 5:
    #     cut.send(3)
