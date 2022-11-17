# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    docsubtitle = scrapy.Field()
    pageurl = scrapy.Field()
    pub_date = scrapy.Field()
    document_number = scrapy.Field()
    contenttype = scrapy.Field()
    source = scrapy.Field()
