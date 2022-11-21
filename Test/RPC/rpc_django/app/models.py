from django.db import models


# Create your models here.

class Task(models.Model):
    task_name = models.CharField(max_length=50, verbose_name='任务名称')
    task_uuid = models.CharField(max_length=50, verbose_name='任务id')
    start_time = models.DateTimeField(verbose_name='开始时间', auto_now=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    status_choice = (
        (0, '未启动'),
        (1, '正在运行'),
        (2, '已完成'),
        (3, '异常'),
    )
    status = models.IntegerField(choices=status_choice, default=0, verbose_name='状态')


class TaskList(models.Model):
    task_name = models.CharField(max_length=50, verbose_name='任务名称')
    task_uuid = models.CharField(max_length=50, verbose_name='任务id')
    start_time = models.DateTimeField(verbose_name='开始时间', auto_now=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    status_choice = (
        (0, '未启动'),
        (1, '正在运行'),
        (2, '已完成'),
        (3, '异常'),
        (4, '正在停止'),
    )
    status = models.IntegerField(choices=status_choice, default=0, verbose_name='状态')
