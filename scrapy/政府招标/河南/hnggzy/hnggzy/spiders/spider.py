import scrapy


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = ['www.hnggzy.com']
    start_urls = ['http://www.hnggzy.com/EpointWebBuilder/rest/frontAppCustomAction/getPageInfoListNewYzm']
    
    data = 'siteGuid=7eb5f7f1-9041-43ad-8e13-8fcb82ea831a&categoryNum=002002&kw=&startDate=&endDate=&pageIndex=4&pageSize=8&jytype='
    
    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], method='POST', body=self.data,
                             callback=self.parse)
    
    def parse(self, response):
        print(response.text)


# 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
