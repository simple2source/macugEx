import os
import io
import json
import uuid
import shutil
import datetime
import threading
import random
import zipfile
import requests
import pystache
import logging
import socket
from kazoo.client import KazooClient
from kazoo.recipe.watchers import ChildrenWatch
from .command import Command


class Listener:
    def __init__(self, hosts, root, workspace='/tmp'):
        self.zk = KazooClient(hosts=hosts)
        self.root = root
        self.workspace = os.path.abspath(workspace)
        self.tasks = []
        self.event = threading.Event()
        self.hostname = os.uname().nodename

    def get_task(self, task_id):
        node = os.path.join(self.root, 'tasks', task_id, 'targets', self.hostname)
        lock_node = os.path.join(node, 'lock')
        lock = self.zk.Lock(lock_node, self.hostname.encode())
        with lock:
            data, _ = self.zk.get(node)
        return json.dumps(data.decode())

    def set_status(self, task_id, status):
        node = os.path.join(self.root, 'tasks', task_id, 'targets', self.hostname)
        lock_node = os.path.join(node, 'lock')
        lock = self.zk.Lock(lock_node, self.hostname.encode())
        with lock:
            self.zk.set(node, status.encode())
        signal_node = os.path.join(self.root, 'signal', task_id)
        self.zk.set(signal_node, uuid.uuid4().bytes)

    def get_job_server_list(self):
        node = os.path.join(self.root, 'job_server')
        return [self.zk.get(os.path.join(node, x))[0] for x in self.zk.get_children(node)]

    def get_log_server_list(self):
        node = os.path.join(self.root, 'log_server')
        result = []
        for server in self.zk.get_children(node):
            address, port = server.split(':')
            result.append((address, int(port)))
        return result

    def render(self, params):
        for root, _, files in os.walk('.'):
            for tmpl in [f for f in files if f.endswith('.tmpl')]:
                path = os.path.join(root, tmpl)
                with open(path, 'r') as f:
                    content = f.read()
                    rendered = pystache.render(content, params)
                    with open(path.replace('.tmpl', ''), 'w') as w:
                        w.write(rendered)

    def _send_log(self, task_id, cmd, seq=1):
        log_server = random.choice(self.get_log_server_list())
        s = socket.socket()
        s.connect(log_server)
        s.send(task_id.encode())
        s.send(b'\n')
        s.send(self.hostname.encode())
        s.send(b'\n')
        s.send('{0}'.format(seq))
        s.send(b'\n\n')
        for buf in cmd.out_stream():
            s.send(buf)
        s.close()

    def send_log(self, task_id, cmd):
        seq = 1
        while not cmd.finish:
            t = threading.Thread(target=self._send_log, args=(task_id, cmd, seq))
            t.start()
            t.join()
            seq += 1

    def schedule(self, task_id):
        task = self.get_task(task_id)
        job_server = random.choice(self.get_job_server_list())
        # http://xxx.xxx.xx.xxx/packages/
        # magedu/test-job
        # http://xxx.xxx.xx.xxx/packages/magedu/test-job.zip
        url = '{0}/{1}.zip'.format(job_server, task_id['job_id'])
        response = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        workspace = os.path.join(self.workspace, task_id)
        os.makedirs(workspace)
        os.chdir(workspace)
        z.extractall()
        try:
            self.render(task.get('params', {}))
        except Exception as e:
            logging.error(e)
            self.set_status(task_id, 'F')
            return
        os.chmod('./run.sh', 0o755)
        cmd = Command('run.sh', workspace, timeout=task.get('timeout', 0))
        self.set_status(task_id, 'R')
        cmd.exec()
        self.send_log(task_id, cmd)
        cmd.wait()
        if cmd.success:
            self.set_status(task_id, 'S')
        else:
            self.set_status(task_id, 'F')

    def run(self):
        while not self.event.is_set():
            if len(self.tasks) > 0:
                task_id = self.tasks.pop(0)
                try:
                    self.schedule(task_id)
                finally:
                    shutil.rmtree(os.path.join(self.workspace, task_id))
            else:
                self.event.wait(1)

    def watch(self, tasks):
        new_tasks = set(tasks).difference(self.tasks)
        self.tasks.extend(new_tasks)
        return not self.event.is_set()

    def start(self):
        self.zk.start()
        node = os.path.join(self.root, 'agents', self.hostname)
        self.zk.ensure_path(node)
        tasks_node = os.path.join(node, 'tasks')
        self.zk.ensure_path(tasks_node)
        self.zk.create(os.path.join(node, 'alive'), str(datetime.datetime.now().timestamp()).encode(), ephemeral=True)
        ChildrenWatch(self.zk, tasks_node, self.watch)
        threading.Thread(target=self.run, name='task-runner').start()

    def shutdown(self):
        self.event.set()

    def join(self):
        self.event.wait()
