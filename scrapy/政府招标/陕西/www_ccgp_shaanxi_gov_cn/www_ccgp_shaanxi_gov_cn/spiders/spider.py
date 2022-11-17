# http://www.ccgp-shaanxi.gov.cn/
import scrapy, pymysql, time
from www_ccgp_shaanxi_gov_cn.redis_conn import redis_conn
from www_ccgp_shaanxi_gov_cn.data_process import *
from www_ccgp_shaanxi_gov_cn.items import Item
from www_ccgp_shaanxi_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-shaanxi.gov.cn'
    redis_name = '政府招标:' + host
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
    start_urls = [
        'http://www.ccgp-shaanxi.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=a7a15d60-de5b-42f2-b35a-7e3efc34e54f&channel=1eb454a2-7ff7-4a3b-b12c-12acc2685bd1&currPage=&pageSize=10&noticeType=001011,001012,001013,001014,001016,001019&regionCode=610001&purchaseManner=&title=&openTenderCode=&purchaseNature=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime&cityOrArea=', # 采购公告
        'http://www.ccgp-shaanxi.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=a7a15d60-de5b-42f2-b35a-7e3efc34e54f&channel=1eb454a2-7ff7-4a3b-b12c-12acc2685bd1&currPage=&pageSize=10&noticeType=001021,001022,001023,001024,001025,001026,001029,001006&regionCode=610001&purchaseManner=&title=&openTenderCode=&purchaseNature=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime&cityOrArea=', # 结果公告
        'http://www.ccgp-shaanxi.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=a7a15d60-de5b-42f2-b35a-7e3efc34e54f&channel=1eb454a2-7ff7-4a3b-b12c-12acc2685bd1&currPage=&pageSize=10&noticeType=001031,001032&regionCode=610001&purchaseManner=&title=&openTenderCode=&purchaseNature=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime&cityOrArea=', # 更正公告
        'http://www.ccgp-shaanxi.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=a7a15d60-de5b-42f2-b35a-7e3efc34e54f&channel=1eb454a2-7ff7-4a3b-b12c-12acc2685bd1&currPage=&pageSize=10&noticeType=001004,001006&regionCode=610001&purchaseManner=&title=&openTenderCode=&purchaseNature=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime&cityOrArea=', # 终止公告
    ]
    start_pages = [2665, 2917, 603, 215]
    headers = {}

    def start_requests(self):
        for i in range(4):
            condition = True
            for page in range(1, self.start_pages[i]+1):
                url = self.start_urls[i].replace('currPage=', f'currPage={page}')

                query = get_link_json(url=url)['data']
                for data in query:
                    pageurl = data['pageurl']
                    lurl = 'http://www.ccgp-shaanxi.gov.cn' + pageurl
                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break
                    # pass

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h1[@class='info-title']")
            date = result.dpath("//div[@class='info-source']//span[@id='noticeTime']", rule=None)
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
            # print(item)
            yield item

        except Exception as e:
            print(e)




############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
