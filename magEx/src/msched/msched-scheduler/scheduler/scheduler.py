import os
import json
import logging
import uuid
import threading
from collections import defaultdict
from kazoo.client import KazooClient
from kazoo.recipe.watchers import ChildrenWatch


class Scheduler:
    def __init__(self, hosts, root):
        self.zk = KazooClient(hosts=hosts)
        self.root = root
        self.event = threading.Event()

    def start(self):
        self.zk.start()
        node = os.path.join(self.root, 'signal')
        ChildrenWatch(self.zk, node, self.run)

    def get_task_info(self, task_id):
        node = os.path.join(self.root, 'tasks', task_id)
        data, _ = self.zk.get(node)
        return json.loads(data.decode('utf-8'))

    def get_targets(self, task_id):
        node = os.path.join(self.root, 'tasks', task_id, 'targets')
        return self.zk.get_children(node)

    def get_target_status(self, task_id, target):
        node = os.path.join(self.root, 'tasks', task_id, 'targets', target)
        data, _ = self.zk.get(node)
        return data.decode('utf-8')

    def get_targets_status(self, task_id):
        targets = self.get_targets(task_id)
        status = ((target, self.get_target_status(task_id, target)) for target in targets)
        result = defaultdict(set)
        for s in status:
            result[s[1]].add(s[0])
        return result, targets

    def copy_task_to_agent(self, task_id, target, task):
        target_node = os.path.join(self.root, 'tasks', task_id, 'targets', target)
        lock_node = os.path.join(target_node, 'lock')
        lock = self.zk.Lock(lock_node)
        with lock:
            data = json.dumps(task)
            node = os.path.join(self.root, 'agents', target, 'tasks', task_id)
            try:
                self.zk.create(node, data.encode('utf-8'))
                self.zk.set(target_node, b'W')
            except Exception as e:
                logging.error(e)
                self.zk.set(target_node, b'F')
                self.zk.set(os.path.join(self.root, 'signal', task_id, uuid.uuid4().bytes))

    def set_task_status(self, task_id, status):
        node = os.path.join(self.root, 'callback', task_id)
        self.zk.create(node, status.encode())

    def run(self, tasks):
        for task_id in set(tasks):
            self.schedule(task_id)
        return not self.event.is_set()

    def schedule(self, task_id):
        node = os.path.join(self.root, 'tasks', task_id)
        lock_node = os.path.join(node, 'lock')
        self.zk.ensure_path(lock_node)
        lock = self.zk.Lock(lock_node)
        try:
            if not lock.acquire(False):
                return
            task = self.get_task_info(task_id)
            status, targets = self.get_targets_status(task_id)
            fail_rate = len(status['F']) / len(targets)
            if fail_rate > task.get('fail_rate', 0):
                self.set_task_status(task_id, 'F')
                return
            count = task.get('concurrent', 1) - (len(status['R']) + len(status['W']))
            can_schedule_count = min(count, len(status['N']))
            if can_schedule_count > 0:
                schedule_list = list(status['N'])[:can_schedule_count]
                for target in schedule_list:
                    self.copy_task_to_agent(task_id, target, task)
            if len(status['N']) + len(status['W']) + len(status['R']) == 0:
                self.set_task_status(task_id, 'S')
        finally:
            lock.release()

    def join(self):
        self.event.wait()

    def shutdown(self):
        self.event.set()
        self.zk.stop()
        self.zk.close()