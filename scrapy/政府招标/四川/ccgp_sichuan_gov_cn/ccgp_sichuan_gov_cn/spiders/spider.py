import scrapy
from ..redis_conn import redis_conn
from ..data_process import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-sichuan.gov.cn'
    condition = True

    def start_requests(self):
        url_index = [1195, 14, 904, 437, 210]
        for i in range(5):
            for page in range(url_index[i]):
                if self.condition is True:
                    url_list = [
                        f'http://www.ccgp-sichuan.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=10&noticeType=00101',
                        # 采购公告
                        f'http://www.ccgp-sichuan.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=10&noticeType=001052,001053,00105B',
                        # 资格预审公告
                        f'http://www.ccgp-sichuan.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=10&noticeType=00102',
                        # 中标（成交）公告
                        f'http://www.ccgp-sichuan.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=10&noticeType=00103',
                        # 更正公告
                        f'http://www.ccgp-sichuan.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=10&noticeType=001004,001006']
                    # 废标（终止）公告
                    yield scrapy.Request(url=url_list[i], callback=self.lparse)
                else:
                    break

    def lparse(self, response):
        item = {}
        data = response.json().get('data', None)
        conn = redis_conn()
        if data is not None:
            for query in data:
                htmlpath = 'http://www.ccgp-sichuan.gov.cn/freecms' + query['htmlpath']
                pagesource = query.get('content', None)
                title = query.get("title", None)
                date = query.get("noticeTime", None)
                result = conn.find_data(value=htmlpath)
                if result is False:
                    content_result = process_content_type(C=pagesource)

                    item['host'] = self.host
                    item['pageurl'] = htmlpath
                    item['docsubtitle'] = title
                    item['publishdate'] = date
                    item['contenttype'] = content_result
                    item['pagesource'] = pagesource
                    yield item
                else:
                    print('已存在:', htmlpath)
                    self.condition = False


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
