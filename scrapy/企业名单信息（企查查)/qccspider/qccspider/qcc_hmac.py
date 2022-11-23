#!/usr/bin/env python
# coding=utf-8
import execjs
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


def getownershipstructuremix(keyno, tid):
    item = {}
    # key1 = 'iLAgi8QLN4kiBl468vlNkQgAk4NL84LNlrgWiLAgi8QLN4kiBl468vlNkQgAk4NL84LNlrgW'
    key1 = 'iLAgiWL4Ligk4i46Lkgigk4Billv6lL18Kik8kL8rWKALKAikN66L1vvWNiLLW1ALBlgvWlWlAiLAgiWL4Ligk4i46Lkgigk4Billv6lL18Kik8kL8rWKALKAikN66L1vvWNiLLW1ALBlgvWlWlA'
    # text1 = '/api/charts/getownershipstructuremix{"keyno":"%s","level":1}' % keyno
    text1 = '/api/datalist/touzilist?keyno=%s&pageindex=4{}' % keyno
    text2 = '/api/datalist/touzilist?keyno=%s&pageindex=4pathString{}%s' % (keyno, tid)
    k1 = hmac_demo(key1, text1)[8:28]
    k2 = hmac_demo(key1, text2)
    item[k1] = k2
    return item


def getequityinvestment(keyno, tid):
    item = {}
    key1 = 'iLAgi8QLN4kiBl4lKLg4lgv1lk4rlv4iLAgi8QLN4kiBl4lKLg4lgv1lk4rlv4'
    text1 = '/api/charts/getequityinvestment{"keyno":"%s"}' % keyno
    text2 = '/api/charts/getequityinvestmentpathString{"keyno":"%s"}%s' % (keyno, tid)
    k1 = hmac_demo(key1, text1)[8:28]
    k2 = hmac_demo(key1, text2)
    item[k1] = k2
    return item


"""对外投资"""


def outbound(keyno: str = None, pageindex: str = None, tid: str = None, ):
    """
    outbound('6fd1ea84db38609f091e64530e904ce9', '7', 'c7471078d8d101a605235f57d5887e4d')
    :param keyno: 企业id
    :param pageindex: 对外投资页码
    :param tid: window.tid
    :return:
    """
    qcc_dict = {}
    with open('qcchmac.js', 'r')as f:
        qcc_encode = f.read()
    ctx = execjs.compile(qcc_encode)
    e = f"/api/datalist/touzilist?keyno={keyno}&pageindex={pageindex}"
    result = ctx.call('r', e)
    text1 = '/api/datalist/touzilist?keyno=%s&pageindex=%s{}'% (keyno, pageindex)
    text2 = '/api/datalist/touzilist?keyno=%s&pageindex=%spathString{}%s' % (keyno, pageindex, tid)
    k1 = hmac_demo(result, text1)[8:28]
    k2 = hmac_demo(result, text2)
    qcc_dict[k1] = k2
    print(qcc_dict)
    return qcc_dict


if __name__ == "__main__":
    # tid = 'c7471078d8d101a605235f57d5887e4d'
    # keyno = 'abc50fc7ac1d549540f6339b22d60aad'
    # k1 = getequityinvestment(keyno, tid)
    # k2 = getownershipstructuremix(keyno, tid)
    # print(k1)
    # print(k2)
    outbound('6fd1ea84db38609f091e64530e904ce9', '7', 'c7471078d8d101a605235f57d5887e4d')
