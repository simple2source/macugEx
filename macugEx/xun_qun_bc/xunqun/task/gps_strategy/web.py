# -*- coding: utf-8 -*-
"""
腕表gps策略web界面
"""
try:
    import ujson as json
except ImportError:
    import json

from flask import Flask, request, render_template
from loop import get_task_data_list, get_task_total, add_task, del_task
from core.db import db

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/tasking_watch', methods=['GET'])
def tasking_watch():
    num = int(request.args.get('num', 10))
    page = int(request.args.get('page', 0))
    return json.dumps(get_task_data_list(page, num))


@app.route('/tasking_count', methods=['GET'])
def tasking_count():
    return str(get_task_total())


@app.route('/tasking_operate', methods=['POST'])
def tasking_operate():
    operate = request.form.get('operate')
    imei = request.form.get('imei')
    if not operate:
        return 'need operate paramter'
    if not imei:
        return 'need imei paramter'
    if operate == 'add':
        result = db.watch.update_one({'_id': imei}, {'$set': {'gps_strategy': 'test'}})
        if result.modified_count:
            add_task(imei, 'test')
    if operate == 'del':
        result = db.watch.update_one({'_id': imei}, {'$unset': {'gps_strategy': 1}})
        if result.modified_count:
            del_task(imei)
    return 'success'


@app.route('/tasking_record/<imei>', methods=['GET'])
def tasking_record(imei):
    num = int(request.args.get('num', 10))
    page = int(request.args.get('page', 0))
    result = db.watch_gps_loger.find({'imei': imei}, {'_id': 0}).sort('timestamp', -1).skip(page * num).limit(num)
    return json.dumps(list(result))


@app.route('/tasking_record_count/<imei>', methods=['GET'])
def tasking_record_count(imei):
    return str(db.watch_gps_loger.find({'imei': imei}).count())
