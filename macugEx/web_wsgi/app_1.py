# -*- coding:utf-8 -*-
import webob


def application(environ, start_response):
    # environ is wsgiref get client env to input application args
    # request
    request = webob.Request(environ)
    param = request.params
    body = request.body
    print(param, body)

    # start_response to return header
    # response
    response = webob.Response()
    response.body = 'hello {}'.format('webob')
    response.status_code = 200
    response.content_type = 'text/plain'
    return response(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 9001, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
