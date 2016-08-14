import json
import uuid
from scheduler import Scheduler

if __name__ == '__main__':
    from kazoo.client import KazooClient
    import sys
    task = {
        'job_id': 'test'
    }
    task_id = uuid.uuid4().hex
    print(task_id)
    target = 'test'
    zk = KazooClient()
    zk.start()
    zk.ensure_path('/msched/agents/{0}/tasks'.format(target))
    zk.ensure_path('/msched/tasks/{0}'.format(task_id))
    zk.set('/msched/tasks/{0}'.format(task_id), json.dumps(task).encode())
    zk.ensure_path('/msched/tasks/{0}/targets/{1}'.format(task_id, target))
    zk.set('/msched/tasks/{0}/targets/{1}'.format(task_id, target), b'N')
    zk.ensure_path('/msched/signal/{0}'.format(task_id))
    if len(sys.argv) >= 1:
        sys.exit()
    sched = Scheduler(zk, 'msched')
    sched.watch()
    try:
        sched.join()
    except KeyboardInterrupt:
        sched.shutdown()

