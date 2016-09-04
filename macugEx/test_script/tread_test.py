from Queue import Queue
import threading

lock = threading.Lock()
ab = 0


def change():
	global ab
	print lock.acquire()
	try:
		ab += 1
	finally:
		lock.release()

if __name__ == '__main__':
	for i in range(4):
		p = threading.Thread(target=change)
		p.start()
	print ab