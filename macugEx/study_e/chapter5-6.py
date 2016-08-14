# -*- coding:utf-8 -*-
from functools import wraps
import time
import random
import os

# 写一个装饰器，对函数的部分或者全部参数做类型检查


def type_check(fn):
	@wraps(fn)
	def decorator(*args, **kwargs):
		for arg in args:
			print type(arg)
		for kwarg in kwargs.values():
			print type(kwarg)
		ret = fn(*args, **kwargs)
		return ret
	return decorator


@type_check
def arg1(a, b, c='33', d=55):
	print a, b, c, d


# 自己实现partial函数

def partial(fn, *args, **kwargs):
	def wrap(*args, **kwargs):
		return fn(*args, **kwargs)
	return wrap

# 写一个函数，判断两个字典是否相等，字典的value可能为
# 数字、字符串、元组、列表、集合和字典。 如果value为列表和字典，需要判断其中每个元素是否相等


def dict_equal(d1, d2):
	v1 = d1.values()
	v2 = d2.values()
	if v1 == v2:
		print 'equal'

# 模拟一个数据源不断的产生数值，求一段时间内，最大的K个元素


def produce(n=100):

	def pro(fn):
		@wraps(fn)
		def decorator(lst=None, **kwargs):
			lst = []
			t1 = time.time()
			t2 = kwargs.get('t')
			while True:
				lst.append(random.randint(0, n))
				time.sleep(0.5)
				if time.time() - t1 - float(t2) > 0:
					break

			ret = fn(lst, **kwargs)
			return ret
		return decorator
	return pro


@produce(n=9999)
def max_k(lst, t=10, k=7):
	lst.sort()
	print lst[-k:-1]

max_k(t=10, k=5)

# 实现os.walk 方法


def walk_1(path):
	# breadth-first
	dirs = [path]
	files = []
	while dirs:
		cur = dirs.pop()
		for f in os.listdir(cur):
			if os.path.isdir(os.path.join(cur, f)):
				dirs.append(os.path.join(cur, f))
				files.append(os.path.join(cur, f))
			else:
				files.append(f)
	print files


def walk(path, l2=None):
	if l2 is None:
		l2 = []
	l1 = os.listdir(path)
	for f in l1:
		if os.path.isdir(os.path.join(path, f)):
			l2.append(os.path.abspath(os.path.join(path, f)))
			return walk(os.path.join(path, f))
		else:
			l2.append(f)
	print l2


# 实现一个优先队列，由用户指定比较函数


# 实现tail -f的功能