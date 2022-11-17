import redis, requests
from fake_useragent import UserAgent

class UserAgentDownloadMiddleware(object):
    """
    随机使用 User Agent 中间件
    """
    def process_request(self, request, spider):
        """
        每次请求都会添加一个随机的 UA
        :param request:
        :param spider:
        :return:
        """
        user_agent = UserAgent().random
        request.headers['User-Agent'] = user_agent


class ProxyMiddleware(object):
    def __init__(self):
        pass

    def process_request(self,request, spider):
        dont_retry = request.meta.get('dont_retry', False)
        get_proxy = self.get_proxy().get('http',None)
        if dont_retry:
            print('代理正在使用：', get_proxy)
            request.meta['retry_times'] += 1
            request.meta['proxy'] = get_proxy
            return
        else:
            print('代理正在使用：', get_proxy)
            request.meta['proxy'] = get_proxy
            request.meta['retry_times'] = 1

    def process_response(self, request, response, spider):
        # retry_times是请求次数
        retry_times = request.meta['retry_times']
        if response.status != 200:
            if retry_times > 3:
                print(response.url,'当前已请求3次，放弃请求:')
                return response
            else:
                print('响应正在尝试ip：',response.url)
                new_request = request.copy()
                new_request.dont_filter = True
                new_request.meta['dont_retry'] = True
                return new_request
        return response


    def get_proxy(self):
        url = "http://182.92.156.157:7388/pachong_api"
        payload = {
            "proxy_type": 3,
            "spider_type": 2,
        }
        response = requests.request("POST", url, data=payload)
        proxies = response.json()['msg'][0]
        return proxies
