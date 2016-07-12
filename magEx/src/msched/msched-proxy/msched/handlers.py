import os
import uuid
import json
from tornado.web import RequestHandler
from tornado.web import HTTPError
from tornado.options import options
from kazoo.exceptions import NoNodeError
from .mixins import RestMixin


class TaskHandler(RestMixin, RequestHandler):
    def get(self, task_id, *args):
        node = os.path.join(options.root, 'tasks', task_id)
        try:
            data, _ = self.application.zk.get(node)
            task = json.loads(data.decode())
            targets_node = os.path.join(node, 'targets')
            targets = self.application.zk.get_children(targets_node)
            targets_status = {}
            for target in targets:
                status, _ = self.application.zk.get(os.path.join(targets_node, target))
                targets_status[target] = status.decode()
            self.jsonify(code=200, task=task, targets=targets_status)
        except NoNodeError:
            raise HTTPError(status_code=404, reason='task {0} not found'.format(task_id))

    def post(self, *args):
        if len(args) == 0:
            task_id = uuid.uuid4().hex
        else:
            task_id = args[0]
        node = os.path.join(options.root, 'tasks', task_id)
        if self.application.zk.exists(node):
            message = 'task {0} exist'.format(task_id)
            raise HTTPError(status_code=409, log_message=message, reason=message)
        payload = self.get_payload()
        task = payload.get('task', {})
        if 'job_id' not in task.keys():
            raise HTTPError(status_code=400, reason='job_id is required')
        targets = payload.get('targets', [])
        if len(targets) < 1:
            raise HTTPError(status_code=400, reason='targets is required')
        self.application.zk.ensure_path(node)
        self.application.zk.set(node, json.dumps(task).encode())
        targets_node = os.path.join(node, 'targets')
        self.application.zk.ensure_path(targets_node)
        for target in targets:
            self.application.zk.create(os.path.join(targets_node, target), b'N')
        self.application.zk.create(os.path.join(options.root, 'signal', task_id), uuid.uuid4().bytes)
        self.jsonify(code=200, task_id=task_id)


class TasksHandler(RestMixin, RequestHandler):
    def get(self):
        node = os.path.join(options.root, 'tasks')
        self.jsonify(code=200, tasks=self.application.zk.get_children(node))