#!/usr/bin/env python
# coding=utf-8

# hmac_demo.py HMAC算法
# 与hashlib不同之处在于多了key

import hmac

tid = 'a026f74acbc7e5aab3c6d6b42e3547cf'  # 浏览器环境window.tid

def hmac_demo(key=None, text=None, digestmod=None):
    '''

    :param digestmod:加密类型，默认MD5， 可选
    MD5, SHA1 SHA224 SHA256 SHA384 SHA512
    :return:
    '''
    # 加密

    key = bytes(key, 'utf-8')
    text = bytes(text, 'utf-8')
    h = hmac.new(key, digestmod='SHA512')
    h.update(text)
    h_str = h.hexdigest()
    return h_str

def getownershipstructuremix(keyno):
    item = {}
    key1 = 'iLAgi8QLN4kiBl468vlNkQgAk4NL84LNlrgWiLAgi8QLN4kiBl468vlNkQgAk4NL84LNlrgW'
    text1 = '/api/charts/getownershipstructuremix{"keyno":"%s","level":1}' % keyno
    text2 = '/api/charts/getownershipstructuremixpathString{"keyno":"%s","level":1}%s' % (keyno, tid)
    k1 = hmac_demo(key1, text1)[8:28]
    k2 = hmac_demo(key1, text2)
    item[k1] = k2
    return item

def getequityinvestment(keyno):
    item = {}
    key1 = 'iLAgi8QLN4kiBl4lKLg4lgv1lk4rlv4iLAgi8QLN4kiBl4lKLg4lgv1lk4rlv4'
    text1 = '/api/charts/getequityinvestment{"keyno":"%s"}' % keyno
    text2 = '/api/charts/getequityinvestmentpathString{"keyno":"%s"}%s' % (keyno, tid)
    k1 = hmac_demo(key1, text1)[8:28]
    k2 = hmac_demo(key1, text2)
    item[k1] = k2
    return item


if __name__ == "__main__":
    keyno = '7d2ff2d16325bdc9e1a4e93b6f2f3132'
    k1 = getequityinvestment(keyno)
    k2 = getownershipstructuremix(keyno)
    print(k1)
    print(k2)



