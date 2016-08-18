# -*- coding:utf-8 -*-

import re
import sys
import datetime
import threading
import requests
"""version 2,对数据进行流式处理，先进行聚合后入influxdb"""

o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* \[(?P<time>.*)\] "(?P<method>\w+) '
			r'(?P<url>[^\s]*)(?P<version>[\w|/\.\d]*)" (?P<status>\d{3}) (?P<length>\d+) "(?P<referer>[^\s]*)" '
			r'"(?P<ua>.*)"')


def read_log(path):
	event = threading.Event()
	offset = 0
	while not event.is_set():
		with open(path) as f:
			f.seek(offset)
			yield from f
			offset = f.tell()
		event.wait(0.1)


def parse(path):
	for line in read_log(path):
		m = o.search(line)
		if m:
			data = m.groupdict()
			yield data


def agg(path, interval=10):
	count = 0
	error = 0
	traffic = 0
	start = datetime.datetime.now()
	for item in parse(path):
		count += 1
		traffic += int(item['length'])
		if item['status'] >= 300:
			error += 1
		current = datetime.datetime.now()
		if (current - start) >= interval:
			error_rate = error / count
			send(count, traffic, error_rate)
			error = 0
			count = 0
			traffic = 0
			start = current


def send(count, traffic, error_rate):
	line = 'access_log count={},traffic={},error_rate={}'.format(count, traffic, error_rate)
	res = requests.post('http://127.0.0.1:8086/write', data=line, params={'db': 'lines'})
	if res >= 300:
		print(res.content())


if __name__ == '__main__':
	agg(sys.argv[1])



