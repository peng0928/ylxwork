import scrapy, pymysql, time
from redis_conn import redis_conn
from ..data_process import *

from ggzy_guiyang_gov_cn.settings import BOT_NAME


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = ''
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',
        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # CONCURRENT_REQUESTS_PER_DOMAIN = 16
        # CONCURRENT_REQUESTS_PER_IP = 16
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    def start_requests(self):
        data = 'title=&origin=&inDates=&channelId=151&ext='
        for page in range(1, 2):
            url = f'http://ggzyjy.shandong.gov.cn/queryContent_{page}-jyxxgk.jspx'
            yield scrapy.Request(url=url, body=data, headers=self.headers, method='POST', callback=self.lparse)
            time.sleep(3)

    def lparse(self, response):
        lurl = response.xpath("//div[@class='article-list3-t']/a/@href").getall()
        for query in lurl:
            print(query)

