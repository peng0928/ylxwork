# -*- coding: utf-8 -*-
# @Date    : 2022-12-28 14:14
# @Author  : chenxuepeng
# # task01
from celery_app import cel
import os
from scrapy import cmdline


@cel.task()
def send_spider(res):
    print(os.getcwd())
    if 'test01' in os.getcwd():
        cls = '''scrapy crawl spider -a method=['"GET"'] -a content_name=[""] -a content_value=[""] -a listing_url=['"https://www.runoob.com/python3/python3-att-dictionary-update.html"'] -a host=['runoob'] -a pucode=['runoob'] -a listing_name=['"链接"'] -a listing_value=[""] -a listing_filter=['"过滤器"'] -a nextpage_name=['xpath'] -a nextpage_value=[''] -a startpage=['0'] -a endpage=['5']'''
        os.system(cls)
        return "完成向%s发送邮件任务" % res

    else:
        os.chdir('test01')
        print(os.getcwd())
        cls = '''scrapy crawl spider -a method=['"GET"'] -a content_name=[""] -a content_value=[""] -a listing_url=['"https://www.runoob.com/python3/python3-att-dictionary-update.html"'] -a host=['runoob'] -a pucode=['runoob'] -a listing_name=['"链接"'] -a listing_value=[""] -a listing_filter=['"过滤器"'] -a nextpage_name=['xpath'] -a nextpage_value=[''] -a startpage=['0'] -a endpage=['5']'''
        os.system(cls)
        return "完成向%s发送邮件任务" % res


