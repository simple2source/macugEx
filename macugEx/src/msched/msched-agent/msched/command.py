import os
import fcntl
import subprocess
import select
import threading


class Command:
    def __init__(self, script, cwd, timeout=None):
        self.script = script
        self.workspace = os.path.abspath(cwd)
        self.timeout = timeout
        self.proc = None
        # self.buffer = io.BytesIO(initial_bytes=1024 * 1024 * 1024)

    def exec(self):
        if self.proc is not None:
            raise Exception('is running')
        os.chdir(self.workspace)
        self.proc = subprocess.Popen(['/bin/bash', '-c', os.path.join(self.workspace, self.script)],
                                     start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def wait(self):
        if self.proc is None:
            raise Exception('not running')
        try:
            self.proc.wait(self.timeout)
        except subprocess.TimeoutExpired:
            self.proc.terminate()

    @property
    def output(self):
        if self.proc is None:
            raise Exception('not running')
        out = self.proc.stdout
        fl = fcntl.fcntl(out, fcntl.F_GETFL)
        fcntl.fcntl(out, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        return out

    @property
    def success(self):
        return self.proc is not None and self.proc.poll() == 0

    @property
    def finish(self):
        return self.proc is not None and self.proc.poll() is not None

    def out_stream(self):
        if self.proc is None:
            raise Exception('not running')
        while self.proc.poll() is None:
            r = select.select([self.output], [], [])[0][0]
            if r:
                yield r.read()

if __name__ == '__main__':
    def p(cmd):
        for buf in cmd.out_stream():
            print(buf)

    cmd = Command('sleep.sh', cwd='.', timeout=2)
    cmd.exec()
    t = threading.Thread(target=p, args=(cmd, ))
    t.start()
    cmd.wait()
    print(cmd.success)