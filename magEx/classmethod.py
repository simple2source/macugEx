#-*- coding:utf-8 -*-
import urllib

class Bird(object):
	__name = 'alice'
	def get_name(self):
		return self.__name

	def set_name(self):
		self.name = 'cunbi'
		return self.name

class member(object):
	count = 0
	def init(self):
		member.count += 1

a1= member()

print a1.count
a2= member()
a2.count = 'maxxx'
print a2.init()
print a2.count
print member.count
a3= member()
print a3.count
print member.count
r=urllib.quote_plus('广州')
print r