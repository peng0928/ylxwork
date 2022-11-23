import os
from multiprocessing import Process
def kill_pid(pid):
    pid = pid
    cmd = 'taskkill /f /t /pid ' + str(pid)
    os.system(cmd)

# kill_pid(1116)
# import os
# os.system('taskkill /im chromedriver.exe /F')
# os.system('taskkill /im chrome.exe /F')
