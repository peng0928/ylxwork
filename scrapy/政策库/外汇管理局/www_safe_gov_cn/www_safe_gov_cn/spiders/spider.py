import scrapy
from www_safe_gov_cn.data_process import *

class SpiderSpider(scrapy.Spider):
    name = 'safespider'
    start_urls = ['https://www.safe.gov.cn/safe/zcfg/index.html']

    def start_requests(self):
        for page in range(1,3):
            if page > 1:
                url = self.start_urls[0].replace('index', f'index_{page}')
            else:
                url = self.start_urls[0]
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        result = response.xpath("//div[@class='list_conr']/ul/li/dt/a/@href").getall()
        for url in result:
            url = 'https://www.safe.gov.cn' + url
            yield scrapy.Request(url=url, callback=self.cparse)

    def cparse(self, response):
        result = Xpath(response.text)
        item = {}
        title = result.xpath("//div[@class='detail_tit']")
        pudate = result.xpath("//div[@class='condition']/ul/li[4]/dd")
        document_number = result.xpath("//span[@id='wh']")
        content = result.xpath("//div[@id='content']")
        item['pudate'] = pudate
        item['title'] = title
        item['document_number'] = document_number
        item['content'] = content
        print(item)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
