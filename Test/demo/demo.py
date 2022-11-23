import os
from multiprocessing import Process
def kill_pid(pid):
    pid = pid
    cmd = 'taskkill /pid ' + str(pid) + ' /f'
    os.system(cmd)

kill_pid(16696)