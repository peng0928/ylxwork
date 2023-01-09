# -*- coding: utf-8 -*-
# @Date    : 2023-01-09 09:40
# @Author  : chenxuepeng

"""XPATH"""
shareholder_xpath = "//section[@id='hkpartner']/div[@class='tcaption']/h3[@class='title']//text()|//section[@id='partner']//h3[@class='title']//text()"
outbound_xpath = "//section[@id='touzilist']//h3[@class='title']//text()"