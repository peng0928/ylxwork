import redis
from .useragent import *

class ProxyMiddleware():

    def process_request(self,request, spider):
        dont_retry = request.meta.get('dont_retry', False)
        if dont_retry:
            request.meta['proxy'] = 'http://tps163.kdlapi.com:15818'
            request.meta['user-agent'] = get_ua()
            request.meta['retry_times'] += 1
            print('代理正在使用：')
            return
        else:
            request.meta['proxy'] = 'http://tps163.kdlapi.com:15818'
            request.meta['user-agent'] = get_ua()
            request.meta['retry_times'] = 1
            print('代理正在使用：')

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



