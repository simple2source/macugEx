# -*- coding:utf-8 -*-

import time
import threading
from flask import Flask, g, session, request, current_app
from werkzeug.routing import Rule
from flask_apscheduler import APScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.url_map.add(Rule('/index', endpoint='haha'))

scheduler = BackgroundScheduler()
scheduler.start()
print(scheduler.state)


@app.before_first_request
def init():
    g.name = 'wuuuuu'
    print(g.name)
    # session['scheduler'] = scheduler


@app.endpoint('haha')
def my_index():
    return 'my index endpoint'


@app.route('/thr')
def thr():
    name = request.args.get('name')
    async_task(name)
    return name


@app.route('/<string:wwx>')
def wx(wwx):
    print(g.name)
    return wwx


# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def pa(path):
#     print(path)
#     scheduler.add_job(tick, 'date', run_date='2017-1-6 14:02:14', args=(path,))
#
#
# @app.route('/<word>', defaults={'word': 'bird'})
# def word_up(word):
#     scheduler.add_job(tick, 'date', run_date='2017-1-6 14:06:14', args=(word,))
#     scheduler.add_job(tick, 'date', run_date='2017-1-6 14:06:04', args=('info',))
#     return word

def async_task(name):
    t = threading.Thread(target=tick, args=(name, threading.current_thread().name), name=threading.Thread.name)
    t.start()


def tick(path, t_name):
    # application = current_app._get_current_object()
    # with application.app_context():
    time.sleep(10)
    print('------------>', str(time.time()), path, t_name)


if __name__ == '__main__':
    app.run()
