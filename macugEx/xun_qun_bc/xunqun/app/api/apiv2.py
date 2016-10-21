# -*- coding: utf-8 -*-
"""
v2版api实现,接口数据与v1返回方式不一样
用'api_<URL>'开头的函数,挂载到 '/v2/<URL>'
"""
from __future__ import absolute_import
from flask import request, Response
from functools import wraps
from static.define import *
from . import form
from .tools import *


def succed(data=None):
    r = Response(headers=[('Content-Type', 'application/json')])
    if data is not None:
        if isinstance(data, (list, tuple)):
            r.data = json.dumps({'status': 200, 'array': data})
        else:
            r.data = json.dumps({'status': 200, 'object': data})
    else:
        r.data = '{"status":200}'
    return r


def failed(code=0, info=None):
    r = Response(headers=[('Content-Type', 'application/json')])
    if info:
        if isinstance(info, (list, tuple)):
            error_key, debug = info
            r.data = '{"status":300,"error":%d,"field":"%s","debug":"%s"}}' % (code, error_key, debug.replace('"', "'"))
        else:
            r.data = '{"status":300,"error":%d,"debug":"%s"}}' % (code, info.replace('"', "'"))
    else:
        r.data = '{"status":300,"error":%d}' % code
    return r


def validate_decorator(validator):
    def decorator(func):
        @wraps(func)
        def apiv2_request_wrapper(*args, **kwargs):
            request_form = request.json if request.mimetype == 'application/json' else request.form if \
                request.form else json.loads(request.data) if request.data else {}
            status, data = validator.validate(request_form)
            if status:
                if 'session' in data:
                    user_id = get_session_user_id(data['session'])
                    if not user_id:
                        return failed(E_session)
                    data['session_user_id'] = user_id
                kwargs['data'] = data
                return func(*args, **kwargs)
            else:
                return failed(E_params, data)

        return apiv2_request_wrapper

    return decorator


@validate_decorator(form.LastVersion())  # 查询APP版本
def api_last_version(data):
    version = db.version.find_one({'platform': data['platform']}, sort=[('_id', -1)])
    if version:
        number = version['number']
        name = version['name']
        url = android_file_path % version['file_id']
        log = version['log']
    else:
        number = 0
        name = ''
        url = ''
        log = ''
    return succed({
        'version': number,
        'name': name,
        'url': url,
        'log': log,
    })
