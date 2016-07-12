import os
import json
import logging
from base64 import urlsafe_b64encode, urlsafe_b64decode
from tornado.web import RequestHandler, HTTPError
from kazoo.exceptions import NoNodeError


class RestMixin:
    def jsonify(self, **kwargs):
        self.set_header('content-type', 'application/json')
        self.write(json.dumps(kwargs))

    def get_payload(self):
        try:
            return json.loads(self.request.body.decode())
        except Exception as e:
            raise HTTPError(400, log_message=str(e))

    def _handle_request_exception(self, e):
        if isinstance(e, HTTPError):
            self.set_status(e.status_code, reason=e.reason)
            self.jsonify(code=e.status_code, message=e.reason)
            self.finish()
            return
        self.set_status(500, reason=str(e))
        self.jsonify(code=e.status_code, message=str(e), exception=e.__class__)


class WatcherHandler(RestMixin, RequestHandler):
    def post(self, *args, **kwargs):
        payload = self.get_payload()
        try:
            filename = urlsafe_b64encode(payload['filename'].encode())
            app_id = payload['app_id']
            self.application.zk.ensure_path(os.path.join(self.application.options.root, app_id, filename.decode()))
            self.jsonify(code=200, message='{0} added'.format(payload['filename']))
        except KeyError:
            raise HTTPError(400, reason='arguments error')
        except Exception as e:
            raise HTTPError(500, log_message=str(e), reason=str(e))

    def delete(self, *args, **kwargs):
        filename = urlsafe_b64encode(self.get_argument('filename').encode()).decode()
        app_id = self.get_argument('app')
        recursive = self.get_argument('recursive', None) is not None
        try:
            path = os.path.join(self.application.options.root, app_id, filename)
            logging.info(path)
            self.application.zk.delete(path,
                                       recursive=recursive)
            self.jsonify(code=200, message='{0} deleted'.format(self.get_argument('filename')))
        except NoNodeError:
            raise HTTPError(404, reason='{0} not found'.format(self.get_argument('filename')))
        except Exception as e:
            raise HTTPError(500, log_message=str(e), reason=str(e))

    def get(self, *args, **kwargs):
        app_id = self.get_argument('app')
        node = os.path.join(self.application.options.root, app_id)
        files = [urlsafe_b64decode(x).decode() for x in self.application.zk.get_children(node)]
        self.jsonify(code=200, files=files)


class RuleHandler(RestMixin, RequestHandler):
    def post(self, *args, **kwargs):
        payload = self.get_payload()
        try:
            raw_name = payload.pop('name')
            name = urlsafe_b64encode(raw_name.encode()).decode()
            filename = urlsafe_b64encode(payload.pop('filename').encode()).decode()
            app_id = payload.pop('app_id')
            for file in self.application.zk.get_children(os.path.join(self.application.options.root, app_id)):
                if filename != file:
                    if name in self.application.zk.get_children(os.path.join(self.application.options.root, app_id, file)):
                        raise HTTPError(400, reason='{0} exist')
            node = os.path.join(self.application.options.root, app_id, filename, name)
            self.application.zk.create(node, json.dumps(payload).encode())
            self.jsonify(code=200, message='created')
        except HTTPError as e:
            raise e
        except AttributeError as e:
            raise HTTPError(400, reason=str(e))
        except Exception as e:
            raise HTTPError(500, reason=str(e))

    def delete(self, *args, **kwargs):
        filename = urlsafe_b64encode(self.get_argument('filename').encode()).decode()
        app_id = self.get_argument('app')
        name = urlsafe_b64encode(self.get_argument('name').encode()).decode()
        node = os.path.join(self.application.options.root, app_id, filename, name)
        self.application.zk.delete(node)
        self.jsonify(code=200, message='deleted')

    def get(self, *args, **kwargs):
        name = self.get_argument('name', None)
        app_id = self.get_argument('app')
        filename = urlsafe_b64encode(self.get_argument('filename').encode()).decode()
        if name is None:
            node = os.path.join(self.application.options.root, app_id, filename)
            names = [urlsafe_b64decode(x).decode() for x in self.application.zk.get_children(node)]
            self.jsonify(code=200, rules=names)
        else:
            node = os.path.join(self.application.options.root, app_id, filename, urlsafe_b64encode(name.encode()).decode())
            rule = self.application.zk.get(node)[0]
            logging.info(type(rule))
            logging.info(rule)
            self.jsonify(code=200, rule=json.loads(rule.decode()))