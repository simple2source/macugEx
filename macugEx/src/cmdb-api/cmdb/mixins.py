import json
from tornado.web import HTTPError
from .exceptions import EntityError, SchemaError


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
        if isinstance(e, (EntityError, SchemaError)):
            self.set_status(400, reason=str(e))
            self.jsonify(code=400, message=str(e))
            self.finish()
            return
        self.set_status(500, reason=str(e))
        self.jsonify(code=e.status_code, message=str(e), exception=e.__class__)
