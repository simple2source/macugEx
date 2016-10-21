# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

app = Blueprint('docs.app', __name__, url_prefix='/docs/app', static_url_path='/docs/app',
                static_folder='static/docs/app')


@app.route('/', methods=['GET'])
def apiv1_handle():
    return render_template('docs/app/index.html')


@app.route('/apiv2/', methods=['GET'])
def apiv2_handle():
    return render_template('docs/app/apiv2/index.html')


@app.route('/push/', methods=['GET'])
def push_handle():
    return render_template('docs/app/push/index.html')


@app.route('/error/', methods=['GET'])
def error_handle():
    return render_template('docs/app/error/index.html')


@app.route('/ChangeLog/', methods=['GET'])
def ChangeLog_handle():
    return render_template('docs/app/ChangeLog/index.html')


@app.route('/other/', methods=['GET'])
def other_handle():
    return render_template('docs/app/other/index.html')


@app.route('/service/', methods=['GET'])
def service_handle():
    return render_template('docs/app/service/index.html')


@app.route('/service/push/', methods=['GET'])
def service_push_handle():
    return render_template('docs/app/service/push/index.html')


@app.route('/service/error/', methods=['GET'])
def service_error_handle():
    return render_template('docs/app/service/error/index.html')


# Blueprint 和主APP共享一个 template_folder, static_folder
# Blueprint 的静态文件需要单独处理
@app.route('/<path:filename>')
def app_doc_static(filename):
    return app.send_static_file(filename)


watch = Blueprint('docs.watch', __name__, url_prefix='/docs/watch', static_url_path='/docs/watch',
                  static_folder='static/docs/watch')


@watch.route('/', methods=['GET'])
def watch_handle():
    return render_template('docs/watch/index.html')


@watch.route('/instruct/', methods=['GET'])
def instruct_handle():
    return render_template('docs/watch/instruct/index.html')


@watch.route('/interface/', methods=['GET'])
def interface_handle():
    return render_template('docs/watch/interface/index.html')


@watch.route('/config/', methods=['GET'])
def config_handle():
    return render_template('docs/watch/config/index.html')


@watch.route('/<path:filename>')
def watch_doc_static(filename):
    return watch.send_static_file(filename)
