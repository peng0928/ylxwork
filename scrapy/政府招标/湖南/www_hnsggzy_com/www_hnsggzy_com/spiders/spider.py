import scrapy
from www_hnsggzy_com.data_process import *
from ..redis_conn import *
from fake_useragent import UserAgent


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.hnsggzy.com'

    headers = {'User-Agent': UserAgent().random}
    condition = True
    def start_requests(self):
        for page in range(1, 2244):
            url = 'https://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=300&channelId=851&ext=&beginTime=&endTime='
            url = url.replace('queryContent-', f'queryContent_{page}-')

            if self.condition is True:
                yield scrapy.Request(url=url, headers=self.headers, callback=self.lparse)
                time.sleep(2)
            else:
                break

    def lparse(self, response):
        conn = redis_conn()
        lresult = response.xpath("//div[@class='article-list3-t']/a/@href").getall()
        for lurl in lresult:

            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, headers=self.headers, callback=self.cparse)
                time.sleep(3)
            else:
                print('已存在:', lurl)
                # self.condition = False

    def cparse(self, response):
        item = {}
        cresult = Xpath(response.text)
        title = cresult.xpath("//div[@class='content-title']")
        date = cresult.dpath("//div[@class='content-title2']", rule=None)
        content = cresult.xpath("//div[@class='content']/div[@class='content-article']",
                                filter="div[@class='content-article']/span|div[@class='div-title2']|script|style")

        content_result = process_content_type(C=content)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = content
        item['contenttype'] = content_result
        yield item


############################ 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
