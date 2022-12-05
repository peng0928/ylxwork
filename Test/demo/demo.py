from concurrent.futures import ThreadPoolExecutor

import requests,time
url_list = ['https://www.cnblogs.com/', 'https://www.csdn.net/']
def get_url(url):
    content = requests.get(url).content.decode()
    print(url+'已获取')

pool = ThreadPoolExecutor(max_workers=1)
future_dict = {}
start = time.time()
for url in url_list:
    future = pool.submit(get_url,url)
    futur2e = pool.submit(get_url,url)
    futur2e2 = pool.submit(get_url,url)
    print(1111, future.done())
    future_dict[url] = future
    print(future_dict['https://www.cnblogs.com/'].done(), 22222)
end = time.time()

