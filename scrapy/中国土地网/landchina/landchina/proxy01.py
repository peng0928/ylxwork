import redis
from .useragent import *
from .encryptions import *
from .data_process import *


class ProxyMiddleware(object):
    def __init__(self):
        pass

    def process_request(self,request, spider):
        dont_retry = request.meta.get('dont_retry', False)
        if dont_retry:
            print('代理正在使用：')
            request.meta['proxy'] = 'http://tps163.kdlapi.com:15818'
            request.meta['retry_times'] += 1
            request.headers['User-Agent'] = get_ua()
            day = get_datetime_now().split('-')[1]
            hash_text = str(request.headers['User-Agent'], 'utf-8') + day + 'list'
            Hash = sha256(hash_text)
            request.headers['Hash'] = Hash
            return
        else:
            request.meta['proxy'] = 'https://tps163.kdlapi.com:15818'
            request.meta['retry_times'] = 1
            print(request.headers)

    def process_response(self, request, response, spider):
        # retry_times是请求次数
        if 'transfer/list' in response.url:
            retry_times = request.meta['retry_times']
            print(response.text)
            total = response.json().get('data').get('total')
            if response.status != 200 or total > 86508:
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

        if 'land/detail' in response.url:
            retry_times = request.meta['retry_times']
            print(len(response.text), response.text)
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





