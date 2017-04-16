# -*- coding:utf-8 -*-

from flask import Flask, session, Response, make_response, request
import flask_sqlalchemy
from pymysql import cursors, connect

app = Flask(__name__)

# con = connect()
# cur = con.cursor()
# cur.execute()



@app.route('/sis')
def sis():
    session['name'] = 'uuui'
    return 'u'


@app.route('/sig')
def sig():
    print(request.cookies)
    print(request.url_root, request.headers['host'])
    print('------', request.cookies.__dict__)
    return 'hs'


@app.route('/six')
def six():
    response = make_response('hahaw'.encode())
    response.set_cookie('year', 'zhangsan')
    return response


class A(object):
    x = 1
    gen = (lambda x: (x for _ in range(10)))(x)

if __name__ == '__main__':
    # app.secret_key = '2e3ew84r4dod'
    # app.session_cookie_name = 'u300000'
    # app.run(host='0.0.0.0', debug=True, port=3001, use_reloader=False)
    print(A.gen)