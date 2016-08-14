# -*- coding:utf-8 -*-
"""
python 实现数据结构-链表
"""


class Node(object):
	"""定义节点和指针，指针指向下一个节点的值 """
	def __init__(self, data):
		self.data = data
		self.next = None


class LinkList(object):
	def __init__(self):
		self.head = None
		self.tail = None

	def append(self, data):
		node = Node(data)
		if self.head is None:
			self.head = node
			self.tail = node
		else:
			self.tail.next = node
			self.tail = node

	def iter(self):
		if not self.head:
			return
		cur = self.head
		yield cur.data
		while cur.next:
			cur = cur.next
			yield cur.data

	def insert(self, idx, data):
		if self.head is None:
			if idx == 0:
				node = Node(data)
				self.head = node
				self.tail = node
			else:
				raise IndexError('index error')
		cur = self.head
		cur_idx = 0
		while cur_idx < idx-1:
			cur = cur.next
			if cur is None:
				raise IndexError('length is short than index')
			cur_idx += 1
		node = Node(data)
		node.next = cur.next
		cur.next = node
		if node.next is None:
			self.tail = node

	def remove(self, idx):
		if self.head is None:
			raise IndexError('empty list')
		cur = self.head
		cur_idx = 0
		while cur_idx < idx-1:
			cur = cur.next
			cur_idx += 1
		cur.next = cur.next.next
		if cur.next is None:
			self.tail = cur

	def __len__(self):
		cur = self.head
		if cur is None:
			return 0
		cur_idx = 1
		while True:
			cur = cur.next
			cur_idx += 1
			if cur.next is None:
				break
		return cur_idx

if __name__ == '__main__':
	L1 = LinkList()
	for i in range(10):
		L1.append(i)

	L1.insert(3, 'www')
	L1.remove(7)
	for x in L1.iter():
		print x
	print len(L1)
	a = []
	print len(a)
	print L1.tail.data