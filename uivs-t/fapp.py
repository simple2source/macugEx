# -*- coding:utf-8 -*-

from flask import Flask, session, Response, make_response, request
import bcrypt
import flask_sqlalchemy
from pymysql import cursors, connect

app = Flask(__name__)

# con = connect()
# cur = con.cursor()
# cur.execute()

glos = 'i am a global'

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
    session['vv'] = 'hell'
    return glos


@app.route('/six')
def six():
    response = make_response('hahaw'.encode())
    response.set_cookie('year', 'zhangsan')
    return response


@app.route('/html/<string:u>-<string:name>')
def html(u, name):
    print(u)
    return '<h1>一个 {}</h1>'.format(name)


@app.route('/t')
def t():
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


def sea():
    name = request.args.get('name')
    print('name  ----> {}'.format(name))
    return name

class A(object):
    x = 1
    gen = (lambda x: (x for _ in range(10)))(x)

if __name__ == '__main__':
    app.secret_key = '2e3ew84r4dod'
    app.session_cookie_name = 'u300000'
    app.run(host='0.0.0.0', debug=True, port=3001, use_reloader=False)