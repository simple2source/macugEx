#!/usr/bin/env python
from livereload import Server, shell

server = Server()
server.watch('./*.rst', shell('make html'))
server.serve(host='0.0.0.0', root='./_build/html')
