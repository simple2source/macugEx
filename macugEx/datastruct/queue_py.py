# -*- coding:utf-8 -*-
"""
python 实现数据结构-队列,python中自带queue数据结构，from queue import Queue
环形队列 ring = deque(maxlen=5) 总是保持5个元素，先进的被覆盖掉
"""


class Node(object):
	def __init__(self, value):
		self.value = value
		self.next = None


class Queue(object):
	def __init__(self):
		self.head = None
		self.tail = None

	def put(self, value):
		node = Node(value)
		if self.head is None:
			self.head = node
			self.tail = node
		node.next = self.tail
		self.tail = node

	def pop(self):
		if self.head is None:
			raise AttributeError('empty')
		node = self.head
		self.head = node.next
		print node.value
		return node.value

if __name__ == '__main__':
	q = Queue()
	for i in range(10):
		q.put(i)
	q.pop()