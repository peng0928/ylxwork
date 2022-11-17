# http://www.ccgp-anhui.gov.cn/home.html
import scrapy, pymysql, time
from www_ccgp_anhui_gov_cn.redis_conn import redis_conn
from www_ccgp_anhui_gov_cn.data_process import *
from www_ccgp_anhui_gov_cn.items import Item
from www_ccgp_anhui_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = ''
    custom_settings = {
        'ITEM_PIPELINES': {
            # f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 0.6,
        'CONCURRENT_REQUESTS': 32,
    }

    ############读取redis数据库爬取############
    # def start_requests(self):
    #     conn = redis_conn()
    #     result = conn.get_data(field=redis_name)  # '政府招标:
    #     for query in result:
    #         url = str(query, encoding='utf-8')
    #         yield scrapy.Request(url=url, callback=self.cparse)
    #
    #
    # def cparse(self, res):
    #     item = Item()
    #     try:
    #         result = Xpath(res.text)
    #         title = result.xpath("")
    #         date = result.dpath("", rule=None)
    #         content = result.xpath("", filter=None)
    #         content_result = process_content_type(C=content)
    #
    #         item['host'] = self.host
    #         item['pageurl'] = res.url
    #         item['docsubtitle'] = title
    #         item['publishdate'] = date
    #         item['contenttype'] = content_result
    #         item['doc_content'] = content
    #         yield item
    #         # print(item)
    #
    #     except Exception as e:
    #         print(e)

    start_pages = []
    headers = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Connection': 'keep-alive',
'Content-Type': 'application/json',
'Host': 'www.ccgp-anhui.gov.cn',
'Origin': 'http://www.ccgp-anhui.gov.cn',
'Referer': 'http://www.ccgp-anhui.gov.cn',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest',
    }
    def start_requests(self):
        for i in range(4):
            for page in range(1, 661):
                data = [
                    # 采购公告
                    '{"leaf":"0","categoryCode":"ZcyAnnouncement2","pageSize":"15","pageNo":"%d"}'%page,
                    # 结果公告
                    '{"leaf":"0","categoryCode":"ZcyAnnouncement4","pageSize":"15","pageNo":"%d"}'%page,
                    # 合同公告
                    '{"leaf":"0","categoryCode":"ZcyAnnouncement5","pageSize":"15","pageNo":"%d"}'%page,
                    # 更正公告
                    '{"leaf":"0","categoryCode":"ZcyAnnouncement3","pageSize":"15","pageNo":"%d"}'%page,
                ]
                url = 'http://www.ccgp-anhui.gov.cn/front/search/category'
                body = data[i]
                # print(body)
                print(body)
                yield scrapy.Request(url=url, headers=self.headers, method='POST', body=body, callback=self.dparse)

    # 链接
    def dparse(self, res):
        try:
            print(res.url)
            hits = res.json()['hits']['hits']
            for data in hits:
                _source = data['_source']
                url = 'http://www.ccgp-anhui.gov.cn' + _source['url']
                publishDate = process_timestamp(_source['publishDate'])
                title = _source['title']
                item = url + '|' + publishDate + '|' + title
                r = redis_conn()
                r.set_add(field=redis_name, value=item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
