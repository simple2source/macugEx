import os
import select
import socketserver


class LogRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        so = self.request.makefile()
        task_id = so.readline().strip()
        print('task_id', task_id)
        hostname = so.readline().strip()
        print('hostname', hostname)
        seq = so.readline().strip()
        print('seq', seq)
        so.readline()
        path = os.path.join(self.server.root, task_id)
        filename = '{0}-{1}.log'.format(hostname, seq)
        os.makedirs(path)
        with open(os.path.join(path, filename), 'w') as f:
            r = select.select([so], [], [])[0][0]
            if r:
                f.write(r.read())
