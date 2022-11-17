# http://www.ccgp-heilongj.gov.cn/
# http://www.ccgp-heilongj.gov.cn/freecms/site/hlj/cggg/index.html
import scrapy, pymysql, time
from www_ccgp_heilongj_gov_cn.redis_conn import redis_conn
from www_ccgp_heilongj_gov_cn.data_process import *
from www_ccgp_heilongj_gov_cn.items import Item
from www_ccgp_heilongj_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-heilongj.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 32
    }

    def start_requests(self):
        for page in range(1, 3452):
            condition = True
            url = f'http://www.ccgp-heilongj.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=94c965cc-c55d-4f92-8469-d5875c68bd04&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=8&noticeType=00101,00103,00102,001032,001004,001006&regionCode=230001&purchaseManner=&title=&openTenderCode=&purchaser=&agency=&purchaseNature=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime'
            query = get_link_json(url)['data']
            for data in query:
                lurl = 'http://www.ccgp-heilongj.gov.cn' + data['pageurl']
                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.con_parse)
                else:
                    print('已存在:', lurl)
                    condition = False
            if condition is False:
                break


    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//p[@class='info-title-especially']")
            date = result.dpath("//span[@id='f_noticeTime']", rule=None)
            content = result.xpath("//div[@id='noticeArea']", filter='script|style')
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
            # print(item)
            yield item

        except Exception as e:
            print(e)





############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
