# -*- coding:utf-8 -*-

from flask import Flask, session, Response, make_response, request
import bcrypt
import flask_sqlalchemy
from pymysql import cursors, connect

app = Flask(__name__)

# con = connect()
# cur = con.cursor()
# cur.execute()


class PrefixMiddleware(object):
    # 给url增加全局前缀
    # https://stackoverflow.com/questions/18967441/add-a-prefix-to-all-flask-routes
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


glos = 'i am a global'


def not_run():
    print('in load not run')


class A(object):
    print('A will new', id(not_run))
    not_run()
    def __init__(self, name='jack', age=18):
        self.name = name
        self.age = age
        print('AAAA00')

    def f1(self):
        print('a f1')


class Mix(object):
    def f(self):
        self.f1()


class B(Mix, A):
    def __init__(self):
        from socketserver import ThreadingTCPServer
        print('b __init__')
        # A.__init__(self)


    def mb(self):
        self.f()

    def f1(self):
        print('b f1')


class C(B):
    ci = True
    def __init__(self):
        print('c -- _init')
        # A.__init__(self)
        super(C, self).__init__()

# a = A()
# b = B()
# print(b.__dict__)
# b.mb()
c = C()
print(c.__dict__)
# c.f()


@app.route('/sis')
def sis():
    global glos
    glos = 't am change '
    session['name'] = 'uuui'
    session['sx'] = 'sx'
    session.clear()
    return glos


@app.route('/siv')
def sig():
    print(request.cookies)
    print(request.url_root, request.headers['host'])
    print('------', request.cookies.keys(), session.get('vv'))
    return glos


@app.route('/vv')
def vv():
    C.ci = 'ciiii'
    print(C.__dict__)
    session['vv'] = 'hell'
    return glos


@app.route('/six')
def six():
    print(C.__dict__)
    response = make_response('hahaw'.encode())
    response.set_cookie('year', 'zhangsan')
    return response


@app.route('/html/<string:u>-<string:name>')
def html(u, name):
    print(u)
    return '<h1>一个 {}</h1>'.format(name)


@app.route('/t')
def t():
    print(session)
    return session['name']


@app.route('/t1')
def t1():
    session['name'] = 'jack'
    return 'jack'


@app.route('/t2')
def t2():
    session['name'] = 'rose'
    return 'rose'


@app.route('/t3')
def t3():
    session.clear()
    return 'clear'


@app.route('/read')
def read():
    name = sea()
    return 'rose'


@app.route('/hi')
def hi():
    name = request.args.get('name')
    print(request.__dict__)
    print(request.method)
    return '<h3>hi {}'.format(name)


@app.route('/ma')
def maw():
    print(request.endpoint)
    page = request.args.get('page', 1, type=int)
    print(type(page), page)
    resp = make_response('<h1>马</h1>', 600)
    resp.set_cookie('answer', 'u17')
    return resp


@app.route('/sa')
def sam():
    session['name'] = 'jack'
    session['age'] = 28
    return 'sam'


@app.route('/wa/')
def wam():
    print(request.cookies)
    return 'wam'


def sea():
    name = request.args.get('name')
    print('name  ----> {}'.format(name))
    return name

class A(object):
    x = 1
    gen = (lambda x: (x for _ in range(10)))(x)

if __name__ == '__main__':
    app.secret_key = '2e3ew8w4r4dod'
    app.session_cookie_name = 'u300000'
    from datetime import timedelta
    # session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)
    print(app.url_map)
    app.run(host='0.0.0.0', debug=True, port=3001, use_reloader=False)
    # use tornado container run flask app
    import tornado.wsgi
    import tornado.httpserver
    import tornado.ioloop
    import tornado.web
    from tornado.wsgi import WSGIContainer
    container = tornado.wsgi.WSGIContainer(app)
    server = tornado.httpserver.HTTPServer(container)
    # server.listen(8000)
    # tornado.ioloop.IOLoop.instance().start()