# -*- coding:utf-8 -*-
import argparse
import threading
from functools import wraps

# - 实现 tail命令， 包括 -n 和 -f 选项， 可以使用argparse实现命令行参数解析


class Tail(object):
	def __init__(self, path):
		self.path = path

	def tail_n(self, n):
		with open(self.path) as f:
			for i in range(n):
				print(f.readline())

	def tail_f(self):
		offset = 0
		while True:
			with open(self.path) as f:
				f.seek(offset)
				for line in f:
					print(line)
				offset = f.tell()
			threading.Event().wait(0.1)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-n", action="store", type=int, help="the exponent")
parser.add_argument("-f", action="store_false", help="process text")
parser.add_argument("file", action="store")
args = parser.parse_args()
print args.n
#
# if __name__ == '__main__':
# 	path = args.file
# 	line = args.n
# 	t = Tail(args.file)
# 	if line:
# 		t.tail_n(line)
# 	else:
# 		t.tail_f()


# - 学习单例设计模式， 并使用装饰器实现单例类

def singleton(cls):
	instance = {}

	@wraps(cls)
	def getinstance(*arg, **kwargs):
		if cls not in instance:
			instance[cls] = cls(*arg, **kwargs)
		return instance[cls]
	return getinstance


@singleton
class Myclass():
	pass

mc = Myclass()

# - 不用内置数据结构，实现栈、队列和列表


# - 实现 staticmethod 装饰器


# - 假设已经存在函数 get_permissions可以获取当前用户的
# 权限列表， 设计一个权限管理类，既可以作为装饰器，对一个函数授权，也可以作为上下文管理，对一段代码授权
#
# 例如
# permissions = get_permissions()
#
# if 'admin' in permissions:
#     ## do somethings
# else:
#    raise Exception('Permissions denied')



# - 实现 contextlib.contextmanager装饰器
