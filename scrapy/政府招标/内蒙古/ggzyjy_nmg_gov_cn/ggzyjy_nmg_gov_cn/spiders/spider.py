import scrapy, requests, json
from scrapy.http import JsonRequest
from lxml import etree
from ggzyjy_nmg_gov_cn.items import Item
from ggzyjy_nmg_gov_cn.pymysql_connection import pymysql_connection
from ggzyjy_nmg_gov_cn.data_process import *
from ggzyjy_nmg_gov_cn.redis_conn import *
from ggzyjy_nmg_gov_cn.useragent import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzyjy.nmg.gov.cn'
    start_urls = ['http://ggzyjy.nmg.gov.cn/jyxx/zfcg/cggg', 'http://ggzyjy.nmg.gov.cn/jyxx/zfcg/zbjggs',
                  'http://ggzyjy.nmg.gov.cn/jyxx/zfcg/gzsx']
    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        'LOG_LEVEL': 'INFO',

    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ggzyjy.nmg.gov.cn',
        'Origin': 'http://ggzyjy.nmg.gov.cn',
        'Referer': 'http://ggzyjy.nmg.gov.cn/jyxx/zfcg/cggg',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_ua(),
    }

    page = [4740, 3489, 1104]
    def start_requests(self):
        for i in range(len(self.page)):
            condition = True
            for p in range(1, self.page[i] + 1):
                body = f"currentPage={str(p)}&time=&industriesTypeCode=&scrollValue=1366&bulletinTitle=&area=&startTime=&endTime="
                url = self.start_urls[i]

                query = post_link(url=url, data=body, rpath="//div[@class='content_right fr']//td[3]/a/@href")
                for item in query:
                    lurl = 'http://' + self.host + item

                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, headers=self.headers, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                    condition = False
                if condition is False:
                    break

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h6[@class='title']")
            date = result.dpath("//div[@class='tip']", rule=None)
            content = result.xpath("//div[@class='detail_contect']", filter="script|style")

            file = result.fxpath("//div[@class='detail_contect']//a")
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
            # print(item)
            yield item

        except Exception as e:
            print(e)

# 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())


