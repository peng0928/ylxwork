from flask import Flask
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from RPC.rpc_spider import *
# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
# 创建线程池执行器
executor = ThreadPoolExecutor(20)
app = Flask(__name__)


@app.route('/jobs')
def run_jobs():
    # 交由线程去执行耗时任务
    executor.submit(long_task, 'hello', 123)
    return 'long task running.'


# 耗时任务
def long_task(arg1, arg2):
    print("args: %s %s!" % (arg1, arg2))
    RpcSpider().open_selenium()
    print("Task is done!")


if __name__ == '__main__':
    app.run()
