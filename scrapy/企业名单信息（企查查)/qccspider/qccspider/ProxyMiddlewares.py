import copy

import redis, requests, re, json
from useragent import get_ua


class Proxy(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = 'http://tps163.kdlapi.com:15818'


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        dont_retry = request.meta.get('dont_retry', False)
        if dont_retry:
            print('正在重试, 代理正在使用')
            print(request.headers)
            return

        else:
            request.meta['retry_times'] = 1
            request.meta['proxy'] = 'http://tps163.kdlapi.com:15818'
            request.headers['User-Agent'] = get_ua()
            request.headers['cookie'] = self.open_cookie()

    def process_response(self, request, response, spider):
        # retry_times是请求次数
        retry_times = request.meta['retry_times']
        if response.status != 200 or '<title>会员登录' in response.text or '<title>405' in response.text:
            if retry_times > 20:
                print(response.url, '当前已请求20次，放弃请求:')
                return response
            else:
                print('响应正在尝试ip：', response.url)
                new_request = request.copy()
                new_request.dont_filter = True
                new_request.meta['dont_redirect'] = True
                new_request.meta['dont_retry'] = True
                # self.save_cookie()
                new_request.headers['cookie'] = self.open_cookie()
                new_request.meta['proxy'] = 'http://tps163.kdlapi.com:15818'
                new_request.meta['retry_times'] += 1
                new_request.headers['User-Agent'] = get_ua()
                return new_request
        return response

    def save_cookie(self):
        item = {'cookie': self.get_cookie()}
        with open('./config.json', 'w')as f:
            f.write(json.dumps(item, ensure_ascii=False))

    def open_cookie(self):
        with open('./config.json', 'r')as f:
            r = json.loads(f.read())
        return r.get('cookie')

    def get_cookie(self):
        url = 'https://www.qcc.com/'
        headers = {
            "Host": "www.qcc.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": get_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        response = requests.get(url=url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'})
        Set_Cookie = response.headers.get('Set-Cookie')
        get_keys = re.findall('(acw_tc|QCCSESSID)(.*?);', Set_Cookie)
        cookies = [''.join(i) for i in get_keys]
        cookie = '; '.join(cookies)
        return cookie
