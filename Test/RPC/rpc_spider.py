# -*- coding: utf-8 -*-
# @Date    : 2022-11-14 09:10
# @Author  : chenxuepeng
import requests, time, os
from selenium import webdriver
from .useragent import get_ua


class RpcSpider(object):

    def __init__(self, url: str = None):
        """

        """
        pid = self.get_os_id()
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')  # 不需要GPU加速
        option.add_argument('--no-sandbox')  # 无沙箱
        option.add_argument('--user-agent={}'.format(get_ua))
        option.add_experimental_option('useAutomationExtension', False)
        option.add_argument("disable-blink-features")
        option.add_argument("disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=option)
        check_url = 'https://www.nmpa.gov.cn/'
        print('正在访问:', check_url)
        self.driver.get(check_url)
        time.sleep(2)
        cookie = self.driver.get_cookies()
        for c in cookie:
            print(c.get('name', None), c.get('value', None))
        print('成功访问:', check_url)
        while True:
            self.open_selenium()
            time.sleep(5)

    def open_selenium(self):
        rpc_code = 'return document.cookie'
        aa = self.driver.execute_script(rpc_code)
        print(aa, 11111111)

    def close_selnium(self):
        self.driver.close()

    def get_os_id(self):
        return os.getppid()

    def kill_pid(self):
        pid = '18344'
        cmd = 'taskkill /pid ' + str(pid) + ' /f'
        os.system(cmd)
        print(pid, 'killed')

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    r = RpcSpider()
