# coding:utf-8
# @Time : 2022/5/10 16:30
# @Author: 皮皮
# @公众号: Python共享之家
# @website : http://pdcfighting.com/
# @File : 头jsrpc.py
# @Software: PyCharm
import requests
import json
import urllib.parse
import time
from lxml import etree
from fake_useragent import UserAgent


def get_sign():
    param_url = "http://127.0.0.1:12080/go?group=para&name=test&action=get_para"
    response = requests.get(url=param_url).text
    response_json = json.loads(response)
    sign = response_json["data"].split(';')[0]
    return sign


def send_request(url, headers=None, data=None):
    res = requests.get(url=url, headers=headers, data=data, proxies={'http': 'http://tps163.kdlapi.com:15818'})
    res.encoding = 'utf-8'
    tree = etree.HTML(res.text)
    title = tree.xpath("//div[@class='text']/a/text()")
    print(title)


if __name__ == '__main__':
    sign = get_sign()
    print(sign)
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": f"acw_tc=3ccdc15c16669449299301194e1038def33752e73b066c9157ac29a3ff37b6; neCYtZEjo8GmO=5W6zSGn4AcVzbFTMHNKqWmloWXEoImQEmUqK0idQinBbB3xMizR7ES8DIkEGv78C3zBp2l9kV2LhDsaSHKO_7nq; {sign}",
        "Host": "www.nmpa.gov.cn",
        "Pragma": "no-cache",
        "Referer": "https://www.nmpa.gov.cn/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UserAgent().random
    }
    url = 'https://www.nmpa.gov.cn/'
    send_request(url=url, headers=headers)
