# -*- coding: utf-8 -*-
# @Date    : 2022-09-01 09:14
# @Author  : chenxuepeng
############################ 启动
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl spider'.split())