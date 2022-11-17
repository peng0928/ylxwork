# 网站链接 http://www.ccgp-qinghai.gov.cn/
import scrapy, pymysql, time, json
from www_ccgp_qinghai_gov_cn.redis_conn import redis_conn
from www_ccgp_qinghai_gov_cn.data_process import *
from www_ccgp_qinghai_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-qinghai.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        # 允许状态码
        'HTTPERROR_ALLOWED_CODES': [403, 404, 400, 500],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1
    }

    start_pages = [558, 230, 660, 660, 660]
    condition = True
    def start_requests(self):
        headers = {
            'Content-Type': 'application/json'
        }
        for i in range(7):
            for page in range(1, self.start_pages[i] + 1):
                data = [
                    # 采购意向
                    '{"pageNo":%d,"pageSize":15,"categoryCode":"ZcyAnnouncement11"}' % page,
                    # 采购公示
                    '{"pageNo":%d,"pageSize":15,"categoryCode":"ZcyAnnouncement1"}' % page,
                    # 公开招标
                    '{"pageNo":%d,"pageSize":15,"categoryCode":"ZcyAnnouncement2"}' % page,
                    # 中标公告
                    '{"pageNo":%d,"pageSize":15,"categoryCode":"ZcyAnnouncement4"}' % page,
                    # 变更公告
                    '{"pageNo":%d,"pageSize":15,"categoryCode":"ZcyAnnouncement3"}' % page,

                ]
                url = 'http://www.ccgp-qinghai.gov.cn/front/search/category'
                body = data[i]
                print('当前:', i, '当前页:', page)
                if self.condition is True:
                    yield scrapy.Request(url=url, method='POST', body=body, headers=headers, callback=self.dparse)
                    time.sleep(3)
                else:
                    break

    def dparse(self, response):
        conn = redis_conn()
        query = response.json()['hits']['hits']
        for item in query:
            lurl = 'http://www.ccgp-qinghai.gov.cn' + item['_source']['url']
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse)
                time.sleep(5)
            else:
                print('已存在:', lurl)
                #self.condition = False

    def cparse(self, response):
        item = {}
        value = response.xpath("//input/@value").getall()[2]
        response_json = json.loads(value)
        title = response_json.get('title', None)
        publishDate = response_json.get('publishDate', None)
        content = response_json.get('content', None)
        result = Xpath(content)
        content = result.xpath("", filter="script|style")
        file = result.fxpath(x="//a")
        filename = file[0]
        filelink = file[1]
        content_result = process_content_type(C=content, F=filelink)

        item['filename'] = filename
        item['filelink'] = filelink
        item['host'] = self.host
        item['pageurl'] = response.url
        item['docsubtitle'] = title
        item['publishdate'] = publishDate
        item['contenttype'] = content_result
        item['doc_content'] = content
        yield item

