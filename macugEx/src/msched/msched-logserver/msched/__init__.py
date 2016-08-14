from socketserver import ThreadingMixIn
from socketserver import TCPServer
from .handlers import LogRequestHandler


class LogServer(ThreadingMixIn, TCPServer):
    pass


def make_server(address, root):
    server = LogServer(server_address=address, RequestHandlerClass=LogRequestHandler)
    setattr(server, 'root', root)
    return server