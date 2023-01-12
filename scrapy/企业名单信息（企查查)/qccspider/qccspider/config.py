# -*- coding: utf-8 -*-
# @Date    : 2023-01-09 09:40
# @Author  : chenxuepeng

"""XPATH"""
shareholder_xpath = "//section[@id='hkpartner']/div[@class='tcaption']/h3[@class='title']//text()|//section[@id='partner']//h3[@class='title']//text()"
outbound_xpath = "//section[@id='touzilist']//h3[@class='title']//text()"
maininfoXpath = "//div[@class='maininfo']"
company_namesXpath = ".//span[@class='copy-title']/a[@class='title copy-value']//text()"
curlXpath = ".//span[@class='copy-title']/a[@class='title copy-value']/@href"
tagsXpath = ".//span[@class='search-tags']/span[@class='m-r-sm']/span/text()"
datatabXpath = "//div[@class='sub-nav']/a[@class='item']/text()"

"""TID"""
TID = 'd4d02f6a0ad33efd0df41412461b0c64'


"""MSG"""
tipMSG = """********如果是第一次运行程序，请重新配置当前目录下面的config.py文件的TID，config.json里的cookie_data********"""
