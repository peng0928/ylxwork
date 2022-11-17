# -*- coding: utf-8 -*-
# @Date    : 2022-11-15 16:02
# @Author  : chenxuepeng

# cmdline.execute('scrapy crawl spider'.split())
len_k = 10
len_v = 10
print(len_k, len_k, type(len_v))
print(len_k != len_v)
if int(len_k) != int(len_v):
    raise ValueError('字段长度不一致,请检测错误!====>>', 1)

else:
    print(0)