# -*- coding: utf-8 -*-
# @Date    : 2022-10-21 14:52
# @Author  : chenxuepeng
import json
import re

import execjs
import requests

header = {
    'Referer': 'https://www.baidu.com/link?url=Wefu8uHqaLSOkDBByP8PLWpW3jLqP9WqP8mhIR_TkcqtSzkh9D4GsGA_YDrs53RVSHeYElCYXhibiD2WfNqmcK&wd=&eqid=a8a1b53a00028f3f000000026253dfea',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
}


def node_js(s, gtk):
    node = execjs.get()
    s1 = node.compile(open('百度翻译逆向.js', encoding='utf-8').read())
    sign = s1.eval('getsign("{}","{}")'.format(s, gtk))
    return sign


def get_token():
    data = {}
    s.get('https://fanyi.baidu.com/?aldtype=16047', headers=header)
    response = s.get('https://fanyi.baidu.com/?aldtype=16047', headers=header)
    r = re.compile("token: '(.*)',")
    g = re.compile('window.gtk = "(.*)";')
    token = r.findall(response.text)
    gtk = g.findall(response.text)
    data['token'] = token
    data['gtk'] = gtk
    return data


def get_data(s1, token, gtk):
    url = 'https://fanyi.baidu.com/v2transapi?from=en&to=zh'
    sign = node_js(s1, gtk)
    zh_en_data = {
        'from': 'zh',
        'to': 'en',
        'query': s1,
        'simple_means_flag': '3',
        'sign': sign,
        'token': token,
        'domain': 'common',
    }
    en_zh_data = {
        'from': 'en',
        'to': 'zh',
        'query': s1,
        'simple_means_flag': '3',
        'sign': sign,
        'token': token,
        'domain': 'common',
    }
    zh_en_info = s.post(url, headers=header, params=zh_en_data).text
    en_zh_info = s.post(url, headers=header, params=en_zh_data).text
    return zh_en_info, en_zh_info


if __name__ == '__main__':
    item = {}
    s = requests.session()
    data = get_token()
    token = data.get('token')[0]
    gtk = data.get('gtk')[0]
    s1 = input('请输入需要查询的单词：')
    info = get_data(s1, token, gtk)
    en_zh_info = json.loads(info[1])
    zh_en_info = json.loads(info[0])
    trans_result_zh = en_zh_info.get('trans_result', None).get('data', None)[0].get('dst', None)
    trans_result_en = zh_en_info.get('trans_result', None).get('data', None)[0].get('dst', None)
    item['中译'] = trans_result_zh
    item['英译'] = trans_result_en
    print(item)
