import redis, time
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
        dont_retry = request.meta.get('dont_retry', False)
        if dont_retry:
            request.meta['retry_times'] += 1
            return
        else:
            request.meta['retry_times'] = 1

    def process_response(self, request, response, spider):
        # retry_times是请求次数
        retry_times = request.meta['retry_times']
        if response.status == 302:
            if retry_times > 3:
                print('当前已请求3次，放弃请求:')
                return response
            else:
                print('休眠90秒')
                time.sleep(90)
                new_request = request.copy()
                new_request.dont_filter = True
                new_request.meta['dont_retry'] = True
                return new_request
        else:
            return response

class ProxyMiddleware(object):
    def __init__(self):
        pass

    def process_request(self,request, spider):
        dont_retry = request.meta.get('dont_retry', False)
        if dont_retry:
            print('代理正在使用：')
            request.meta['retry_times'] += 1
            return
        else:
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



