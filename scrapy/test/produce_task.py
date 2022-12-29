# -*- coding: utf-8 -*-
# @Date    : 2022-12-28 14:14
# @Author  : chenxuepeng
from celery_tasks.task01 import send_spider
import time

start_time = time.time()

result = send_spider.delay("yuan")
print(result.id)

