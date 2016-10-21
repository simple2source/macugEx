# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

app = Blueprint('docs.app', __name__, url_prefix='/docs', static_url_path='/docs',
                static_folder='../docs/_build/html', template_folder='../docs/_build/html')


@app.route('/', methods=['GET'])
def apiv1_handle():
    return render_template('index.html')


@app.route('/<path:filename>')
def app_doc_static(filename):
    return app.send_static_file(filename)
