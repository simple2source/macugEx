# -*- coding:utf-8 -*-
"""
python 实现数据结构-栈,python中可以用列表实现栈的操作
"""


class Node(object):
	def __init__(self, data):
		self.data = data
		self.next = None


class Stack(object):
	def __init__(self):
		self.top = None

	def push(self, data):
		node = Node(data)
		node.next = self.top
		self.top = node

	def pop(self):
		node = self.top
		self.top = node.next
		return node.data

if __name__ == '__main__':
	stack = Stack()
	exp = '({a * [x/(x+y)]}'
	for c in exp:
		if c in '{[(':
			stack.push(c)
		elif c in '}])':
			v = stack.top.data
			if c == '}' and v != '{':
				raise Exception('failed')
			if c == ']' and v != '[':
				raise Exception('failed')
			if c == ')' and v != '(':
				raise Exception('failed')
			stack.pop()
	if stack.top is not None:
		raise Exception('t failed')