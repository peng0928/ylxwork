# -*- coding: utf-8 -*-
# @Date    : 2022-11-14 11:51
# @Author  : chenxuepeng
from flask import *
import os

app = Flask(__name__)


@app.route('/')
def index():
    return '1'


@app.route('/add')
def add():
    # print(os.getcwd())
    os.system('python rpc_spider.py')
    return 'Ok'


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5006,
        debug=True,
    )
