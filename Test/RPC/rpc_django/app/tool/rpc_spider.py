# -*- coding: utf-8 -*-
# @Date    : 2022-11-14 09:10
# @Author  : chenxuepeng
import time, os, json
from selenium import webdriver
from app.tool.useragent import get_ua
from app.tool.redis_conn import *


class RpcSpider(object):

    def __init__(self, url: str = None, task_id: str = None):
        """
        初始化redis
        """
        redisconn = redis_conn(db=1)
        path = f'rpcfile:{task_id}:'

        start_cookie = []
        start_cookie_dict = {}
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')  # 不需要GPU加速
        option.add_argument('--no-sandbox')  # 无沙箱
        option.add_argument('--user-agent={}'.format(get_ua))
        option.add_experimental_option('useAutomationExtension', False)
        option.add_argument("disable-blink-features")
        option.add_argument("disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=option)
        check_url = url
        self.driver.get(check_url)
        # print(os.getppid())

        time.sleep(2)
        cookie = self.driver.get_cookies()
        for c in cookie:
            key, value = c.get('name', None), c.get('value', None)
            start_cookie.append(key + '=' + value)
        start_cookie = '; '.join(start_cookie)
        start_cookie_dict['startcookie'] = start_cookie
        redisconn.set_add(field=path+'fcookie:', value=json.dumps(start_cookie_dict,ensure_ascii=False))
        while True:
            pid = self.get_os_id()
            headers = {}
            code = self.open_selenium()
            headers['cookie'] = code
            headers['pid'] = pid
            redisconn.set_add(field=path + 'config:', value=json.dumps(headers, ensure_ascii=False))
            time.sleep(1)

    def open_selenium(self):
        rpc_code = 'return document.cookie'
        code = self.driver.execute_script(rpc_code)
        return code

    def close_selnium(self):
        self.driver.close()
        self.driver.quit()

    def get_os_id(self):
        return os.getpid()


    def __del__(self):
        print(11)
        self.driver.close()
        self.driver.quit()

import atexit
@atexit.register
def a():
    print('gqqww')

if __name__ == '__main__':
    r = RpcSpider(url='https://www.nmpa.gov.cn/', task_id="48914946-daeb-369a-ac01-17630e3cb74a")
