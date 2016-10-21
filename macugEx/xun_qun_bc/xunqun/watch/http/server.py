# -*- coding: utf-8 -*-
from json import loads
from werkzeug.http import parse_options_header
from werkzeug.wsgi import get_input_stream
from werkzeug.wrappers import Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException


class WatchHttp(object):
    def __init__(self):
        self.url_map = Map()

    def route(self, url):
        def decorate(func):
            self.url_map.add(Rule('/watch/%s' % url, endpoint=url))
            setattr(self, url, func)

        return decorate

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except HTTPException as e:
            return e

    def __call__(self, environ, start_response):
        request = Request(environ)

        content_type, content_charset = parse_options_header(request.environ.get('CONTENT_TYPE', ''))
        if content_type == 'application/json':
            try:
                data = loads(get_input_stream(environ).read(), encoding=content_charset.get('charset'))
            except ValueError:
                data = {}
            request.form = data

        response = self.dispatch_request(request)
        return response(environ, start_response)
