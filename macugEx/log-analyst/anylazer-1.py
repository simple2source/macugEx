# -*- coding:utf-8 -*-

import re
import sys
import pygal
import datetime
"""使用 pygal 画图 version 1,每分钟对时间进行统计流量汇总"""


def read_log(path):
	with open(path) as f:
		for line in f:
			yield line


def parse(path):
	o = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .* .* '
					r'\[(?P<time>.*)\] "(?P<method>\w+) (?P<url>[^\s]*) '
				r'(?P<version>[\w|/\.\d]*)" (?P<status>\d{3}) (?P<length>\d+) '
				r'"(?P<referer>[^\s]*)" "(?P<ua>.*)"')
	for line in read_log(path):
		m = o.search(line.rstrip('\n'))
		if m:
			data = m.groupdict()
			data['time'] = datetime.datetime.strptime(data['time'], '%d/%b/%Y:%H:%M:%S %z')
			yield data


def count(key, data):
	if key not in data.keys():
		data[key] = 0
	data[key] += 1
	return data


def analyze(path):
	ret = {}

	def init_data():
		return{
			'ip': {},
			'url': {},
			'ua': {},
			'status': {},
			'throughput': 0
		}
	for item in parse(path):
		time = item['time'].strftime('%Y%m%d%H%M')
		if item['time'] not in ret.keys():
			ret[time] = init_data()
		count_data = ret[time]
		for key, value in count_data.items():
			if key != 'throughput':
				count_data[key] = count(item[key], value)
		count_data['throughput'] += int(item['length'])
	return ret


def render_line(name, labels, data):
	line = pygal.Line()
	line.title = name
	line.x_labels = labels
	line.add(name, data)
	return line.render()


def render_bar():
	pass


def main():
	data = analyze(sys.argv[1])
	rs = list(data.items())
	rs.sort(key=lambda x: x[0])
	labels = [x[0] for x in rs]
	throughput = [x[1]['throughput'] for x in rs]
	svg = render_line('throughput', labels, throughput)
	with open('throughput.svg', 'w') as f:
		f.write(svg)


if __name__ == '__main__':
	main()