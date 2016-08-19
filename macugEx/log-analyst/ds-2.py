import re
import threading
import datetime
import random


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
			now = datetime.datetime.now()
			data['time'] = now.strftime('%d/%b/%Y:%H:%M:%S %z')
			yield data


def data_source(event, src, *dst):
	files = []
	for path in dst:
		files.append(open(path, 'a'))
	while not event.is_set():
		for item in parse(src):
			line = '{ip} - - [{time}] "{method} {url} {version}" {status} ' \
					'{length} "{referer}" "{ua}"\n'.format(**item)
			f = random.choice(files)
			f.write(line)
			event.wait(0.1)
	for f in files:
		f.close()


if __name__ == '__main__':
	import sys
	e = threading.Event()
	try:
		data_source(e, sys.argv[1], *sys.argv[2:])
	except KeyboardInterrupt:
		e.set()