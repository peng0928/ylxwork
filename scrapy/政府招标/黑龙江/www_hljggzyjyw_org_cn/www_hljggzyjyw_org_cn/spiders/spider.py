# http://www.hljggzyjyw.org.cn/
# http://www.hljggzyjyw.org.cn/jyfwdt/003002/003002002/003002002001/about2.html

import scrapy, pymysql, time
from www_hljggzyjyw_org_cn.data_process import *
from www_hljggzyjyw_org_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.hljggzyjyw.org.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            'www_hljggzyjyw_org_cn.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        'COOKIES_ENABLED': False,
    }
    condition = True
    start_pages = [1317, 453, 977]
    def start_requests(self):
        start_urls = [
            # 政府采购信息-采购/预审公告
            'http://www.hljggzyjyw.org.cn/jyfwdt/003002/003002002/003002002001/about2.html?categoryNum=003002002001&pageIndex=',
            # 政府采购信息-变更公告
            'http://www.hljggzyjyw.org.cn/jyfwdt/003002/003002002/003002002002/about2.html?categoryNum=003002002002&pageIndex=',
            # 政府采购信息-中标结果公示
            'http://www.hljggzyjyw.org.cn/jyfwdt/003002/003002002/003002002004/about2.html?categoryNum=003002002004&pageIndex=',
        ]
        for i in range(3):
            self.condition = True
            for page in range(500, self.start_pages[i]+1):
                lurl = start_urls[i].replace('pageIndex=', f'pageIndex={str(page)}')
                print(lurl)
                if self.condition is True:
                    yield scrapy.Request(url=lurl, callback=self.lparse)
                else:
                    break

    def lparse(self, response):
        links = response.xpath("//div[@class='wb-data-infor']/a/@href").getall()
        conn = redis_conn()
        for lurl in links:
            lurl = 'http://www.hljggzyjyw.org.cn' + lurl
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.dparse)
            else:
                print('已存在:', lurl)
                self.condition = False

    def dparse(self, response):
        item = {}
        cresult = Xpath(response.text)
        title = cresult.xpath("//div[@class='ewb-art']/h2")
        date = cresult.dpath("//div[@class='art-subwpr']/div[@class='art-sub clearfix']")
        content = cresult.xpath("//div[@class='ewb-art-bd']", filter='style|script')
        file = cresult.fxpath("//div[@class='ewb-art-bd']//a")
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

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
