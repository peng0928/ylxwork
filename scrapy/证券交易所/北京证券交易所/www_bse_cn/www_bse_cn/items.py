# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    companyCd = scrapy.Field()
    companyName = scrapy.Field()
    destFilePath = scrapy.Field()
    publishDate = scrapy.Field()
    disclosureTitle = scrapy.Field()
    fileName = scrapy.Field()
    status = scrapy.Field()
    stockName = scrapy.Field()
