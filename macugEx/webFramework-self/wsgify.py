from webob import Request
from functools import wraps


def wsigfy(fn):
    @wraps(fn)
    def wrap(environ, start_response):
        request = Request(environ)
        resp = fn(request)
        return resp(environ, start_response)
    return wrap