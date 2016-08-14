from msched import make_server

server = make_server(('127.0.0.1', 1234), '/tmp')

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.shutdown()