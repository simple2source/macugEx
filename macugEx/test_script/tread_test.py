from Queue import Queue
import threading

a = threading.Thread()
b = threading.Event()
c = threading.Lock()
d = threading.Condition()


class A(object):
	def __init__(self):
		pass

	def __enter__(self):
		print 'ssss'
		return None

	def __exit__(self, *args):
		print 'xxxx'
		return None

a1 = A()
with a1:
	print a1, 'in ov'