#!./python2.7/bin/python
# -*- coding: utf-8 -*-
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SimpleHTTPServer
import multiprocessing
import subprocess
import webbrowser
import atexit
import json
import sys
import re
import os


def web():
    SimpleHTTPServer.SimpleHTTPRequestHandler.protocol_version = "HTTP/1.0"
    httpd = HTTPServer(('', 5600), SimpleHTTPServer.SimpleHTTPRequestHandler)

    print("Serving HTTP on %s port %s ..." % httpd.socket.getsockname())
    httpd.serve_forever()


conf_head = '''\
# -*- coding: utf-8 -*-
#
# engine project configure file
#
import logging
'''


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.is_json = False

        data = ''
        m = re.search('/(\w+)/(\w*)', self.path)
        if m:
            prefix, path = m.groups()
            if prefix == 'check':
                data = self.check(path)
            elif prefix == 'test_mongo':
                data = self.test_mongodb()
            elif prefix == 'runing':
                data = self.runing(path)
            elif prefix == 'start':
                data = self.start(path)

        if not self.is_json:
            self.send_header("Content-type", "text/html; charset=utf-8")
        else:
            self.send_header("Content-type", "application/json; charset=utf-8")
            data = json.dumps(data)

        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def check(self, module_name):
        with open(os.devnull, 'w') as devnull:
            if subprocess.call("python -c 'import %s'" % module_name, shell=True, stderr=devnull) == 0:
                data = "success"
            else:
                data = 'error'
        return data

    def test_mongodb(self):
        p = subprocess.Popen("python ./intro/test_mongo.py", shell=True, stderr=subprocess.PIPE)
        if p.wait() == 0:
            data = "success"
        else:
            data = p.stderr.read()
        return data

    def runing(self, program):
        self.is_json = True
        p = subprocess.Popen("python -c 'import conf;print(conf.%s[\"port\"])'" % program, shell=True,
                             stdout=subprocess.PIPE)
        a = p.stdout.read()
        if not a:
            return {'status': 'bad paramter'}
        port = int(a)
        if sys.platform.startswith('linux'):
            p = subprocess.Popen("netstat -ntlp|grep ':%s'" % port, shell=True, stdout=subprocess.PIPE)
            result = p.stdout.read()
        elif sys.platform == 'darwin':
            p = subprocess.Popen("lsof -iTCP:%s -sTCP:LISTEN" % port, shell=True, stdout=subprocess.PIPE)
            result = p.stdout.read()
        else:
            result = None
        if result:
            return {'status': 'success', 'port': port}
        else:
            return {'status': 'not runing'}

    def start(self, directory):
        subprocess.Popen("cd %s;nohup python run.py %s >/dev/null 2>&1 &" % tuple([directory] * 2), shell=True,
                         close_fds=True)
        return 'success'

    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)

        with open('./conf.py', 'w') as conf_file:
            conf_file.write(conf_head)
            conf_file.write(post_body)

        p = subprocess.Popen('python -c "import conf"', shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.stdout.read(), p.stderr.read()
        if err:
            data = json.dumps({'status': 'error', 'data': err})
        else:
            data = json.dumps({'status': 'success'})
            with open('./conf.example', 'w') as exam_file:
                exam_file.write(post_body)

        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, 200, 'OK'))
        self.wfile.write("Access-Control-Allow-Origin: *\r\n")
        self.wfile.write("Content-type: application/json; charset=utf-8\r\n")
        self.wfile.write("Content-Length: %d\r\n\r\n" % len(data))

        self.wfile.write(data)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def check_exec_prefix():
    if sys.platform.startswith('linux'):
        if os.getenv('PWD') == os.path.dirname(sys.prefix):
            print("SUCCESS  当前 Python 执行环境为项目预先打包的文件夹 python2.7")
        else:
            print("ERROR   当前 Python 执行环境不是项目预先打包的文件 python2.7")
            print("ERROR   请执行 source activate 命令后重试")
            print("ERROR   继续运行需要按文档所示安装项目依赖,否则请退出安装程序")
    else:
        print("INFO    请按文档所示安装项目依赖")


def main():
    try:
        os.stat('./python2.7')
    except OSError:
        try:
            os.stat('./python2.7.tar.bz')
        except OSError:
            if sys.platform.startswith('linux'):
                print("ERROR   当前项目找不到 centos 打包执行环境")
            else:
                print("INFO    请按文档安装项目依赖")
        else:
            print('WARNING  正在解压项目打包的 Python 执行环境')
            status = subprocess.call('tar -jxvf ./python2.7.tar.bz', shell=True)
            if not status:
                print("WARNING  解压成功,如果想使用打包好的 Python 环境")
                print("WARNING  请执行 source activate")
                print("WARNING  之后再运行本程序重试")
            else:
                print("ERROR    解压项目打包环境失败")
        print("WARNING  继续运行需要按文档所示安装项目依赖,否则请退出安装程序")
    else:
        check_exec_prefix()

    p = multiprocessing.Process(target=web)
    p.start()

    atexit.register(lambda: p.terminate())
    if not webbrowser.open("http://127.0.0.1:5600/intro/check.html"):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("aliyun.com",80))
        ip = s.getsockname()[0]
        s.close()
        print("ERROR    请访问 http://%s:5600/intro/check.html 打开安装引导界面。" % ip)

    httpd = ThreadedHTTPServer(('', 5700), MyRequestHandler)
    print("Serving HTTP on %s port %s ..." % httpd.socket.getsockname())
    httpd.serve_forever()


if __name__ == '__main__':
    main()
