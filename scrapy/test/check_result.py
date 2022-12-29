# -*- coding: utf-8 -*-
# @Date    : 2022-12-28 14:13
# @Author  : chenxuepeng
# 消费者
from celery.result import AsyncResult
from celery_tasks.celery_app import cel

async_result = AsyncResult(id='641cca00-d098-419e-906e-bed4aebfbac1', app=cel)

if async_result.successful():
    result = async_result.get()
    print(result)
    # 将结果删除，，执行完成，结果不会自动删除
    # result.forget()
    # 无论现在是什么状态，都要停止
    # result.revoker(terminate=True)
    # 如果还没开始就停止
    result.revoker(terminate=False)
elif async_result.failed():
    print("执行失败")
elif async_result.status == "PENDING":
    print("任务等待中被执行")
elif async_result.status == "RETRY":
    print("任务异常后正在重试")
elif async_result.status == "STARTED":
    print("任务已经开始被执行")