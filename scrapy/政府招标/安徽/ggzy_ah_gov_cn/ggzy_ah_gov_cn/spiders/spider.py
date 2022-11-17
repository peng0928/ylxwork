import scrapy, re
from ..data_process import *
from ..redis_conn import *
from fake_useragent import UserAgent

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzy.ah.gov.cn'
    condition = True

    def start_requests(self):
        url = 'http://ggzy.ah.gov.cn/zfcg/list'
        headers = {'User-Agent': UserAgent().random,
                   'Content-Type': 'application/x-www-form-urlencoded'}
        for page in range(8570, 8571):
            data = f'currentPage={page}&time=&bulletinNature=1&jyptId=&region='
            if self.condition is True:
                yield scrapy.Request(url=url, body=data, headers=headers, method='POST', callback=self.lparse)
            else:
                break

    def lparse(self, response):
        lresult = response.xpath("//li[@class='list-item']/a/@href").getall()
        conn = redis_conn()

        date = response.xpath("//span[@class='date float-r m-r-40']//text()").getall()
        for query in range(len(lresult)):
            guid = re.findall("guid=(.*?)&tender", lresult[query])[0]
            pbdate = date[query]
            lurl = f'http://ggzy.ah.gov.cn/zfcg/newDetailSub?type=bulletin&bulletinNature=1&guid={guid}&statusGuid='

            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse, method='POST', meta={'pbdate': pbdate})
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        item = {}
        result = Xpath(response.text)
        title = result.xpath("//p[@id='title']")
        date = response.meta['pbdate']
        content = result.xpath("//div[@id='content']", filter="script|style")

        file = result.fxpath("//div[@id='content']//a")
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
        yield item