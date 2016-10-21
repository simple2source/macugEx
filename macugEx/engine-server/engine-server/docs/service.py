#!/usr/bin/env python
try:
    from livereload import Server, shell

    live_reload = True
except ImportError:
    from SimpleHTTPServer import SimpleHTTPRequestHandler, BaseHTTPServer

    live_reload = False

import subprocess


def main():
    subprocess.call('make html', shell=True)

    if live_reload:
        server = Server()
        server.watch('./*/*.rst', shell('make html'))
        server.watch('./*.rst', shell('make html'))
        server.serve(host='0.0.0.0', root='./_build/html')
    else:
        SimpleHTTPRequestHandler.protocol_version = "HTTP/1.0"
        httpd = BaseHTTPServer.HTTPServer(('', 5500), SimpleHTTPRequestHandler)
        httpd.serve_forever()


if __name__ == '__main__':
    main()
