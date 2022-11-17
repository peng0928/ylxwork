import scrapy
from www_china_cba_net.data_process import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = [
        'https://www.china-cba.net/Index/lists/catid/16/p/1.html',
        'https://www.china-cba.net/Index/lists/catid/16/p/2.html',
        'https://www.china-cba.net/Index/lists/catid/16/p/3.html',
    ]
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.lparse)

    def lparse(self, response):
        result = response.xpath("//div[@class='q3_r fix']/ul/li/a/@href").getall()
        for urls in result:
            url = 'https://www.china-cba.net' + urls
            print(url)
            yield scrapy.Request(url=url, callback=self.cparse)

    def cparse(self, response):
        result = Xpath(response.text)
        item = {}
        title = result.xpath("//div[@class='d6_tit fix']/h3")
        pudate = result.dpath("//div[@class='d6_d1 fix']")
        content = result.xpath("//div[@id='neirong']")
        item['pudate'] = pudate
        item['title'] = title
        item['content'] = content
        print(item)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())