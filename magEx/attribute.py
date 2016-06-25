# -*- coding:utf-8 -*-
"""
定义python特性、属性和类私有方法
"""


class Element(object):
	def __init__(self, name, symbol):
		self.name = name
		self.symbol = symbol

	@property
	def get_name(self):
		return self.name

	@property
	def set_symbol(self, args):
		self.symbol = args

	# names = property(get_name, set_symbol)


# draw = Element('jack', 'wheel')
#
# print draw.get_name
# draw.symbol = 'circle'
# print draw.symbol


class Foo:
	def __init__(self):
		self.name = 'yoda'
		self.work = 'master'
	@property
	def person(self):
		return self.name,self.work
	@person.setter
	def person(self,value):
		self.name,self.work = value

A3 = Foo()
print A3.person, '----'
A3.person = 'skylaer','programer'
print A3.person