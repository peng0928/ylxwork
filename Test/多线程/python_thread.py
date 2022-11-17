# -*- coding: utf-8 -*-
# @Date    : 2022-10-13 11:02
# @Author  : chenxuepeng
# -*- coding: utf-8 -*-
"""
    1、多线程爬虫
"""
import requests, threading, time, uuid
from bs4 import BeautifulSoup
from config import *
from tool.data_process import *
from txdpy import urljoin


def getResonse(**kwargs):
    """
    uuid = 请求状态码+请求链接+响应长度
    """
    url, encode, lock, l_link_xh, l_lost, l_get = kwargs['url'], kwargs.get('encode', 'utf-8'), kwargs['lock'], kwargs[
        'l_link_xh'], kwargs['l_lost'], kwargs['l_get']
    html = requests.get(url=url)
    html.encoding = encode
    html_text = html.text
    listing_uuid = get_uuid(str(html.status_code), url, str(len(html_text)))

    lock.acquire()
    save_html(name=listing_uuid, html=html_text)
    lock.release()


    # 进入列表页
    lock.acquire()
    html_tree = Xpath(html_text)
    l_link = html_tree.xpath(l_link_xh)
    l_link = [urljoin(url, i) for i in l_link] if l_link != [] else l_link


    if l_link == []:
        l_lost.append(url)
    else:
        l_get.append(l_link)

    lock.release()


def getConResonse(**kwargs):
    """
    uuid = 请求状态码+请求链接+响应长度
    """
    url, encode, lock, l_link_xh, l_lost = \
        kwargs['url'], kwargs.get('encode', 'utf-8'), kwargs['lock'], kwargs['c_link_xh'], kwargs['c_lost']
    html = requests.get(url=url)
    html.encoding = encode
    html_text = html.text
    listing_uuid = get_uuid(str(html.status_code), url, str(len(html_text)))

    lock.acquire()
    save_html(name=listing_uuid, html=html_text)
    print(url)
    lock.release()


def save_html(**kwargs):
    name = kwargs['name']
    html = kwargs['html']
    with open(f'./html/{name}.html', 'w', encoding='utf-8')as f:
        f.write(html)


def list_of_groups(init_list, children_list_len):
    list_of_groups = zip(*(iter(init_list),) * children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count != 0 else end_list
    return end_list


def get_uuid(*args):
    args = ''.join(args)
    return uuid.uuid3(uuid.NAMESPACE_DNS, args)


def main(thread_numb=3):
    """
    主函数
    :return:
    """
    l_lost = []
    l_get = []
    start_time = time.time()
    url = [
        'https://www.runoob.com/',
        'https://channel.chinanews.com.cn/u/gn-dyxc.shtml',

    ]
    l_link_xh = "//div[@class='mt17']//li/a/@href|//div[@class='topcon']/a/@href|//div[@class='col middle-column-home']/div/a/@href"

    thread_url_list = list_of_groups(url, thread_numb)

    for thread_url in thread_url_list:
        # 多线程启监控任务
        lock = threading.Lock()
        thread_list = []

        len_thread_url = len(thread_url)
        for i in range(len_thread_url):
            url = thread_url[i]
            thread_kwargs = {
                'url': url,
                'lock': lock,
                'l_link_xh': l_link_xh,
                'l_lost': l_lost,
                'l_get': l_get,
            }
            thread = threading.Thread(target=getResonse, kwargs=thread_kwargs)
            thread_list.append(thread)

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()

    end_time = time.time()

    send_c_thread(l_get)
    print("开始时间:", start_time, '结束时间:', end_time, '总时间:', end_time - start_time)


def send_c_thread(thread_url, **kwargs):
    for thread_url in thread_url:
        thread_url = set(thread_url)
        thread_url = list(thread_url)
        clock = threading.Lock()
        thread_list = []
        len_thread_url = len(thread_url)
        for i in range(len_thread_url):
            url = thread_url[i]
            thread_kwargs = {
                'url': url,
                'lock': clock,
                'c_link_xh': kwargs.get('c_link_xh', ''),
                'c_lost': kwargs.get('c_lost', ''),
            }
            thread = threading.Thread(target=getConResonse, kwargs=thread_kwargs)
            thread_list.append(thread)
        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()


if __name__ == '__main__':
    start_time = time.time()

    main()
    end_time = time.time()


    print("开始时间:", start_time, '结束时间:', end_time, '总时间:', end_time - start_time)