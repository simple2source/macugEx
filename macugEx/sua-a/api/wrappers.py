import logging
import datetime
import decimal
from json import dumps
from functools import wraps

from flask import request
from flask import make_response, current_app
from flask_restful import Resource as BaseResource, Api as BaseApi, OrderedDict, reqparse
from werkzeug.wrappers import Response as ResponseBase
from bson.objectid import ObjectId, InvalidId

__all__ = ['api', 'Resource', 'wrap_object_id', 'wrap_page_num']

try:
    import conf
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import conf


def custom_dumps_fix(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime.datetime):
        if obj.year < 1900:
            return '00-00-00 00:00:00'
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, datetime.date):
        if obj.year < 1900:
            return '00-00-00'
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, datetime.time):
        return obj.strftime('%H:%M')
    if isinstance(obj, decimal.Decimal):
        return "%.2f" % obj
    raise TypeError(repr(obj) + ' is not JSON serializable')


def custom_output_json(data, code, headers=None):
    if current_app.debug:
        dumped = dumps(data, **{
            'indent': 4,
            'sort_keys': True,
            'default': custom_dumps_fix
        }) + "\n"
    else:
        dumped = dumps(data, default=custom_dumps_fix) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp


def turn_off_view_provide_automatic_options(view):
    view.provide_automatic_options = False
    view.methods.append('OPTIONS')
    return view


class Api(BaseApi):
    url_prefix = '/resource'

    def __init__(self):
        super(Api, self).__init__()
        self.resource_class = []
        self.log = logging.getLogger('app')
        self.representations = OrderedDict([
            ('application/json', custom_output_json)
        ])
        # disable resource view's provide_automatic_options
        self.decorators.append(turn_off_view_provide_automatic_options)

    def _init_app(self, app):
        """
        wrap the flask-RESTful Api class to avoid deep error handle stack
        """

        # app.handle_exception = partial(self.error_router, app.handle_exception)
        # app.handle_user_exception = partial(self.error_router, app.handle_user_exception)

        if len(self.resources) > 0:
            for resource, urls, kwargs in self.resources:
                self._register_view(app, resource, *urls, **kwargs)

    def __call__(self, app):
        self.init_app(app)
        return self

    def add_resource(self, resource, *urls, **kwargs):
        if resource not in self.resource_class:
            resource_urls = ['/'.join([self.url_prefix, url.lstrip('/')]) for url in urls]
            if self.app is not None:
                self._register_view(self.app, resource, *resource_urls, **kwargs)
            else:
                self.resources.append((resource, resource_urls, kwargs))
            self.resource_class.append(resource)
        else:
            import traceback
            self.log.warning(
                '\n View function mapping is overwriting an existing endpoint function\n'
                ' --> %s %s %s %s' % traceback.extract_stack()[-2]
            )


api = Api()


class Resource(BaseResource):
    """
    wrap the flask-Restful Resource class to avoid create Resource class pre request.

    but warning about now Resource can't use __init__ function to initialize
    self private data, the init function only available for define global data.
    """

    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        resp = meth(*args, **kwargs)

        if isinstance(resp, ResponseBase):  # There may be a better way to test
            return resp
        return resp

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        v = cls(*class_args, **class_kwargs)
        log = logging.getLogger('app')

        def view(*args, **kwargs):
            try:
                rsp = v.dispatch_request(*args, **kwargs)
                return rsp, 200, {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
                }
            except:
                log.error('\nview:%s\ndata:%s' % (v, request.data), exc_info=True)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods
        return view

    @classmethod
    def options(cls, *args, **kwargs):
        return None


def wrap_object_id(*_ids):
    """
        wrap view function to like:

        @wrap_object_id('userid')
        def get(self, userid):
            assert isinstance(userid, ObjectId)

    """

    def decorator(view):
        @wraps(view)
        def change_str_to_object_id(*args, **kwargs):
            try:
                for _id in _ids:
                    kwargs[_id] = ObjectId(kwargs[_id])
            except InvalidId:
                return {'code': 1001, 'msg': 'invalid company id'}
            return view(*args, **kwargs)

        return change_str_to_object_id

    return decorator


def wrap_page_num(page=0, num=10):
    """
        wrap view function to like:

        @wrap_page_num(0, 10)
        def get(self, userid, page, num):
            assert isinstance(page, float)
            assert isinstance(num, float)

    """

    def decorator(view):
        @wraps(view)
        def get_page_num_to_float(*args, **kwargs):
            try:
                kwargs['page'] = int(request.args.get('page', page))
                kwargs['num'] = int(request.args.get('num', num))
            except ValueError:
                return {'code': 1001, 'msg': 'bad page or num params'}
            return view(*args, **kwargs)

        return get_page_num_to_float

    return decorator
