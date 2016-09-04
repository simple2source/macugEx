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
from concurrent.futures import ProcessPoolExecutor
""" version 4,对数据进行流式处理，多线程的方式，一个线程读一个文件，
	parse 使用多进程的方式进行管理, agg 以多进程的方式处理管理，先进行聚合后入influxdb"""

o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* \[(?P<time>.*)\] "(?P<method>\w+) '
			r'(?P<url>[^\s]*)(?P<version>[\w|/\.\d]*)" (?P<status>\d{3}) (?P<length>\d+) "(?P<referer>[^\s]*)" '
			r'"(?P<ua>.*)"')

event = multiprocessing.Event()
# process event --


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
	t = threading.Thread(target=read_log, name=path, args=(path, q))
	t.start()


def parse(in_que, out_que):
	while not event.is_set():
		line = out_que.get()
		m = o.search(line.rstrip('\n'))
		if m:
			data = m.groupdict()
			in_que.put(data)


def agg(in_queue, out_queue, interval=10):
	count = 0
	traffic = 0
	error = 0
	start = datetime.datetime.now()
	while True:
		item = in_queue.get()
		count += 1
		traffic += int(item['length'])
		if int(item['status']) >= 300:
			error += 1
		current = datetime.datetime.now()
		if (current - start).total_seconds() >= interval:
			out_queue.put((count, traffic, error))
			start = current
			error = 0
			count = 0
			traffic = 0


def agg_manager(parse_que, interval=10):
	queue_list = []
	for i in ['a', 'b', 'c', 'd']:
		out_que = multiprocessing.Queue()
		queue_list.append(out_que)
		ag = multiprocessing.Process(target=agg, name='agg-{}'.format(i), args=(parse_que, out_que, interval))
		ag.start()
	while not event.is_set():
		total_count = 0
		total_traffic = 0
		total_error = 0
		for x in queue_list:
			count, traffic, error = x.get()
			total_count += count
			total_traffic += traffic
			total_error += error
		send(total_count, total_traffic, total_error/total_count)


def send(count, traffic, error_rate):
	line = 'access_log count={},traffic={},error_rate={}'.format(count, traffic, error_rate)
	res = requests.post('http://127.0.0.1:8086/write', data=line, params={'db': 'lines'})
	if int(res.status_code) >= 300:
		print(res.content())


def manage(*paths):
	read_que = multiprocessing.Queue()
	parse_que = multiprocessing.Queue()
	for path in paths:
		read_work(path, read_que)
	for i in [1, 2, 3, 4]:
		p = multiprocessing.Process(target=parse, name='parse-{}'.format(i), args=(parse_que, read_que))
		p.daemon = True
		p.start()
	agg_manager(parse_que)
	while not event.is_set():
		event.wait(10)

if __name__ == '__main__':
	manage(*sys.argv[1:])
