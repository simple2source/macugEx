from uuid import uuid4
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop


class SessionMixin:
    def get_session_id(self):
        session_id = self.get_cookie('session_id')
        if session_id is None:
            session_id = uuid4().hex
            self.set_cookie('session_id', uuid4().hex)
        return session_id

    def session_get(self, name):
        session_id = self.get_session_id()
        return self.application.session.get(session_id, name)

    def session_put(self, name, value):
        session_id = self.get_session_id()
        self.application.session.put(session_id, name, value)

    def session_clean(self):
        session_id = self.get_session_id()
        self.application.session.clean(session_id)


class MainHandler(SessionMixin, RequestHandler):
    def get(self, *args, **kwargs):
        self.session_put('test', 'abc')
        self.write('session test is {0}'.format(self.session_get('test')))


class SessionManager:
    def __init__(self):
        self.session_data = {}

    def get(self, session_id, name):
        return self.session_data.get(session_id, {}).get(name)

    def put(self, session_id, name, value):
        if session_id not in self.session_data.keys():
            self.session_data[session_id] = {}
        self.session_data[session_id][name] = value

    def clean(self, session_id):
        self.session_data.pop(session_id)


def make_app(router, **settings):
    app = Application(router, **settings)
    setattr(app, 'session', SessionManager())
    return app


if __name__ == '__main__':
    app = make_app([(r'/', MainHandler)])
    app.listen(port=8000, address='0.0.0.0')
    IOLoop.current().start()