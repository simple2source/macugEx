# -*- coding:utf-8 -*-

import re
import random
import sys
import os
import datetime
import threading
import requests
import queue
import multiprocessing
""" version 4,对数据进行流式处理，多线程的方式，一个线程读一个文件，先进行聚合后入influxdb
	parse 使用多进程的方式进行管理"""

o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* \[(?P<time>.*)\] "(?P<method>\w+) '
			r'(?P<url>[^\s]*)(?P<version>[\w|/\.\d]*)" (?P<status>\d{3}) (?P<length>\d+) "(?P<referer>[^\s]*)" '
			r'"(?P<ua>.*)"')

event = threading.Event()


def read_log(path, q):
	offset = 0
	while not event.is_set():
		with open(path) as f:
			if offset > os.stat(path).st_size:
				offset = 0
			f.seek(offset)
			for line in f:
				q.put(line)
			offset = f.tell()


def read_work(path, q):
	t = threading.Thread(target=read_log, name=path, args=(q,))
	t.start()


def parse(in_que, out_que):
	while not event.is_set():
		line = out_que.get()
		m = o.search(line.rstrip('\n'))
		if m:
			data = m.groupdict()
			in_que.put(data)


def manage(*paths):
	read_que = multiprocessing.Queue()
	parse_que = multiprocessing.Queue()
	for path in paths:
		read_work(path, read_que)
	for i in [1, 2, 3, 4]:
		p = multiprocessing.Process(target=parse, name='parse-{}'.format(i), args=(parse_que, read_que))
		p.start()
	agg(parse_que)


def agg(q, interval=10):
	count = 0
	traffic = 0
	error = 0
	start = datetime.datetime.now()
	while True:
		item = q.get()
		count += 1
		traffic += int(item['length'])
		if int(item['status']) >= 300:
			error += 1
		current = datetime.datetime.now()
		if (current - start).total_seconds() >= interval:
			error_rate = error / count
			send(count, traffic, error_rate)
			start = current
			error = 0
			count = 0
			traffic = 0


def send(count, traffic, error_rate):
	line = 'access_log count={},traffic={},error_rate={}'.format(count, traffic, error_rate)
	res = requests.post('http://127.0.0.1:8086/write', data=line, params={'db': 'lines'})
	if int(res.status_code) >= 300:
		print(res.content())


if __name__ == '__main__':
	manage(*sys.argv[1:])