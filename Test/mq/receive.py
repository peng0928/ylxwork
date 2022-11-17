import datetime
from apscheduler.schedulers.background import BackgroundScheduler


def job1():
    print('job1')


def job2(x, y):
    print('job2', x, y)


scheduler = BackgroundScheduler()
scheduler.start()


# 每 10 秒运行一次
scheduler.add_job(
    job1,
    trigger='cron',
    second='*/10'
)


