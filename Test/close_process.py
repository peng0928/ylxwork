# -*- coding: utf-8 -*-
# @Date    : 2022-10-19 10:55
# @Author  : chenxuepeng
import psutil, os

process_name = 8652
print(psutil.Process(process_name).name)
os.system('taskkill /f /im %s' % process_name)