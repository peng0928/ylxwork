import scrapy
from scrapy import cmdline
import requests, json
from ggzy_hebei_gov_cn.data_process import *
from ggzy_hebei_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzy.hebei.gov.cn'
    start_urls = ['http://ggzy.hebei.gov.cn/hbjyzx/jydt/001002/001002001/001002001001/2.html']

    condition = True
    def start_requests(self):
        for page in range(1, 3069):
            if page > 1:
                url = self.start_urls[0].replace('2.html', f'{page}.html')
            else:
                url = 'http://ggzy.hebei.gov.cn/hbjyzx/jydt/001002/001002001/001002001001/jyxxList.html'

            if self.condition is True:
                yield scrapy.Request(url=url, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        conn = redis_conn()
        query = response.xpath("//div[@class='ewb-com-block']/a/@href").getall()
        for data in query:
            lurl = 'http://ggzy.hebei.gov.cn' + data

            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.con_parse)
            else:
                self.condition = False
                print('已存在:', lurl)

    def con_parse(self, response):
        item = {}
        result = Xpath(response.text)
        title = result.xpath("//h2[@class='ewb-con-h']")
        date = result.dpath("//div[@class='ewb-bar-info']", rule=None)
        content = result.xpath("//div[@class='ewb-con-p']", filter="script|style")

        # filename = response.xpath("").extract() or None
        # filelink = response.xpath("").extract() or None
        # if filelink is not None and filename is not None:
        #     fileurl = ''
        #     filename = '|'.join(filename)
        #     filelink = fileurl + f'|{fileurl}'.join(filelink)
        # item['filename'] = filename
        # item['filelink'] = filelink
        content_result = process_content_type(C=content, F=None)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = content
        item['contenttype'] = content_result
        print(item)
        # yield item


# 启动
if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
