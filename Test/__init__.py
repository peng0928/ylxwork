# -*- coding: utf-8 -*-
# @Date    : 2022-11-17 23:32
# @Author  : chenxuepeng
import os
def kill_pid(pid):
    pid = pid
    cmd = 'taskkill /pid ' + str(pid) + ' /f'
    os.system(cmd)
kill_pid(12072)