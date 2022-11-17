# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Penalty_date = scrapy.Field()  # 处罚日期
    Penalty_doc_num = scrapy.Field()  # 处罚文书号
    Company_name = scrapy.Field  # 单位名称
    Offences = scrapy.Field  # 违法事由
    Punishment_basis = scrapy.Field  # 处罚依据
    Penalty_content = scrapy.Field  # 处罚内容
    penalty_unit = scrapy.Field  # 处罚单位
    Penalty_amount = scrapy.Field  # 处罚金额
