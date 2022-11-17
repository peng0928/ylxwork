# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Item(scrapy.Item):
    filelink = scrapy.Field()
    filename = scrapy.Field()
    host = scrapy.Field()
    pageurl = scrapy.Field()
    docsubtitle = scrapy.Field()
    publishdate = scrapy.Field()
    doc_content = scrapy.Field()
    contenttype = scrapy.Field()


class ddItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    sourceurl = scrapy.Field()