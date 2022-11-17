

import scrapy


class Item(scrapy.Item):
    host = scrapy.Field()
    filename = scrapy.Field()
    filelink = scrapy.Field()
    pageurl = scrapy.Field()
    docsubtitle = scrapy.Field()
    publishdate = scrapy.Field()
    doc_content = scrapy.Field()
    contenttype = scrapy.Field()