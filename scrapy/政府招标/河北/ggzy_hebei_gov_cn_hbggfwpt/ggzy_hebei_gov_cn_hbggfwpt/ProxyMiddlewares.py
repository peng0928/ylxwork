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
        dont_retry = request.meta.get('dont_retry', False)
        if dont_retry:
            request.meta['retry_times'] += 1
            return
        else:
            request.meta['retry_times'] = 1

    def process_response(self, request, response, spider):
        # retry_times是请求次数
        retry_times = request.meta['retry_times']
        if response.status != 200:
            if retry_times > 3:
                print('当前已请求3次，放弃请求:')
                return response
            else:
                print('休眠180秒')
                time.sleep(180)
                new_request = request.copy()
                new_request.dont_filter = True
                new_request.meta['dont_retry'] = True
                return new_request
        else:
            return response





