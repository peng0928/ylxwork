import scrapy, json
from prec_sxzwfw_gov_cn.items import Item
from prec_sxzwfw_gov_cn.data_process import *
from prec_sxzwfw_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://prec.sxzwfw.gov.cn/jyxxzc/index_1.jhtml']
    host = 'prec.sxzwfw.gov.cn'

    def start_requests(self):
        condition = True
        for page in range(1, 10960):
            if page < 2:
                url = self.start_urls[0]
            else:
                url = self.start_urls[0].replace('index_1', f'index_{str(page)}')
            query = get_link(url, rpath="//div[@class='cs_two_content']/a/@href")
            for lurl in query:
                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.con_parse)
                else:
                    print('已存在:', lurl)
                condition = False
            if condition is False:
                # pass
                break

    def con_parse(self, response):
        item = Item()

        result = Xpath(response.text)
        title = result.xpath("//p[@class='cs_title_P1']")
        date = result.dpath("//p[@class='cs_title_P3']", rule=None)
        content = result.xpath("//div[@class='div-article2']/table[@class='gycq-table']", filter="script|style")

        file = result.fxpath("//table[@class='gycq-table']//a")
        filename = file[0]
        filelink = file[1]

        item['filename'] = filename
        item['filelink'] = filelink
        content_result = process_content_type(C=content, F=filelink)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = content
        item['contenttype'] = content_result
        print(item)
        # yield item

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl spider'.split())