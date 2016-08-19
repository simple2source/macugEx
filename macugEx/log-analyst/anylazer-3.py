# -*- coding:utf-8 -*-

import re
import sys
import os
import datetime
import threading
import requests
import queue
"""version 3,对数据进行流式处理，多线程的方式，一个线程监控一个文件，先进行聚合后入influxdb"""

o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* \[(?P<time>.*)\] "(?P<method>\w+) '
			r'(?P<url>[^\s]*)(?P<version>[\w|/\.\d]*)" (?P<status>\d{3}) (?P<length>\d+) "(?P<referer>[^\s]*)" '
			r'"(?P<ua>.*)"')


def read_log(path, q):
	event = threading.Event()
	offset = 0
	while not event.is_set():
		with open(path) as f:
			if offset > os.stat(path).st_size:
				offset = 0
			f.seek(offset)
			for line in f:
				q.put(line)
			offset = f.tell()


def read_worker(path, q):
	t = threading.Thread(target=read_log, name='read-{}'.format(path), args=(q,))
	t.start()


def parse(*paths):
	q = queue.Queue()
	for path in paths:
		read_worker(path, q)
	while True:
		line = q.get()
		m = o.search(line.rstrip('\n'))
		if m:
			data = m.groupdict()
			yield data


def agg(*paths, **kwargs):
	interval = kwargs.get('interval', 10)
	count = 0
	traffic = 0
	error = 0
	start = datetime.datetime.now()
	for item in parse(*paths):
		count += 1
		traffic += int(item['length'])
		if int(item['status']) >= 300:
			error += 1
		current = datetime.datetime.now()
		if (current - start).seconds() >= interval:
			error_rate = error / count
			send(count, traffic, error_rate)
			start = current
			error = 0
			count = 0
			traffic = 0


def send(count, traffic, error_rate):
	line = 'access_log count={},traffic={},error_rate={}'.format(count, traffic, error_rate)
	res = requests.post('http://127.0.0.1:8086/write', data=line, params={'db': 'lines'})
	if int(res.status_code()) >= 300:
		print(res.content())


if __name__ == '__main__':
	agg(*sys.argv[1:])