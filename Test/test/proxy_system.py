import time

def set_proxy():
    from winproxy import ProxySetting
    p = ProxySetting()
    """设置系统代理"""
    p.enable = True
    proxy = 'tps163.kdlapi.com:15818'
    print(proxy)
    p.server = proxy
    p.registry_write()

def close_proxy():
    """关闭系统代理"""
    from winproxy import ProxySetting
    p = ProxySetting()
    p.enable = False
    p.registry_write()

if __name__ == '__main__':
    close_proxy()
    # while True:
        # set_proxy()
        # time.sleep(5)
        # close_proxy()
