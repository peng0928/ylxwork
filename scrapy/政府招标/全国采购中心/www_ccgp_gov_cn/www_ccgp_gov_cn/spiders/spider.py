import scrapy, requests, html
from scrapy import cmdline
from www_ccgp_gov_cn.items import Item
from www_ccgp_gov_cn.data_process import *
from www_ccgp_gov_cn.redis_conn import redis_conn
from lxml import etree
from fake_useragent import UserAgent

class SpiderSpider(scrapy.Spider):
    name = 'ccgpgovspider'
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'FEED_EXPORT_ENCODING ': 'utf-8',
        'ITEM_PIPELINES': {
            'www_ccgp_gov_cn.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        }
    }
    host = 'www.ccgp.gov.cn'
    datenow = get_datetime_now(rule='%Y:%m:%d')
    condition = True
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'Hm_lvt_9459d8c503dd3c37b526898ff5aacadd=1664255380,1665284653,1665365161; Hm_lvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1663308005,1665215584,1665449108; Hm_lpvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1665458565; JSESSIONID=PwbFU5xKAsoTNwzFjHaJmmZmbSFG2uWg0yMxXzwBeBnPhTHMmUj3!-1275288944; Hm_lpvt_9459d8c503dd3c37b526898ff5aacadd=1665462949',
        'Host': 'search.ccgp.gov.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    def start_requests(self):
        # 全国政府采购网   全国人大机关采购中心
        for l in range(3700, 4000):
            print(l)
            start_url = f'http://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index={l}&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=&dbselect=bidx&kw=&start_time=2022%3A03%3A29&end_time={self.datenow}&timeType=5&displayZone=&zoneId=&pppStatus=0&agentName='
            if self.condition is True:
                yield scrapy.Request(url=start_url, callback=self.lparese, headers=self.headers)
            else:
                break

    def lparese(self, response):
        tree = response.xpath("//div[@class='vT-srch-result-list']//li/a/@href").getall()
        for lurl in tree:
            conn = redis_conn()
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.con_parse)
            else:
                print('已存在', lurl)
                #self.condition = False

    def con_parse(self, response):

        item = {}
        try:
            result = Xpath(response.text)
            title = result.xpath("//h2[@class='tc']")
            date = result.dpath("//span[@id='pubTime']", rule=None)
            content = result.xpath(
                "//div[@class='vT_detail_main']/div[@class='vT_detail_content w760c']|//div[@class='vT_detail_main']/div[@class='table']|//div[@class='vF_detail_content']",
                filter="td[@class='bid_attachtab_content']|script|style")
            content_result = process_content_type(C=content)

            filename = response.xpath("//a[@class='bizDownload']/text()").extract() or None
            filelink = response.xpath("//a[@class='bizDownload']/@id").extract() or None
            if filelink is not None and filename is not None:
                fileurl = 'http://download.ccgp.gov.cn/oss/download?uuid='
                filename = '|'.join(filename)
                filelink = fileurl + f'|{fileurl}'.join(filelink)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            item['filename'] = filename
            item['filelink'] = filelink
            item['pagesource'] = response.text
            yield item
            # print(item)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    cmdline.execute('scrapy crawl ccgpgovspider'.split())