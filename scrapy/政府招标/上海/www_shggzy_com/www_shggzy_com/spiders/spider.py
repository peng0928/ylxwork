# https://www.shggzy.com/
# https://www.shggzy.com/jyxxzc.jhtml?cExt=eyJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL2p5eHh6YyIsInBhZ2VObyI6MSwiZXhwIjoxNjYxMzM4NzkwNzA5fQ.pPrUDj9CcxygpVF8ymRctIQf20I_SicNHI4g7kwrcIU
import scrapy, pymysql, time
from www_shggzy_com.redis_conn import redis_conn
from www_shggzy_com.data_process import *
from www_shggzy_com.items import Item
from www_shggzy_com.settings import *


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
    #     # print(item)
    #
    #     except Exception as e:
    #         print(e)

    start_pages = []

    def start_requests(self):
        for page in range(1,5):
            if page > 1:
                url = f'https://www.shggzy.com/jyxxzc_{page}.jhtml?cExt=eyJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL2p5eHh6YyIsInBhZ2VObyI6MSwiZXhwIjoxNjYxMzM4NzkwNzA5fQ.pPrUDj9CcxygpVF8ymRctIQf20I_SicNHI4g7kwrcIU'
            else:
                url = 'https://www.shggzy.com/jyxxzc.jhtml?cExt=eyJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL2p5eHh6YyIsInBhZ2VObyI6MSwiZXhwIjoxNjYxMzM4NzkwNzA5fQ.pPrUDj9CcxygpVF8ymRctIQf20I_SicNHI4g7kwrcIU'
            # yield scrapy.Request(url=url, callback=self.dparse)
            print(url)
    # 链接
    def dparse(self, res):
        print(res.url)
        try:
            r = redis_conn()
            query = res.xpath("//div[@class='gui-title-bottom']/ul/li/@onclick").extract()
            for item in query:
                item = re.findall("'(.*?)'", item)[0]
                url = 'https://www.shggzy.com' + item
                # print(url)
                r.set_add(field=redis_name, value=url)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
