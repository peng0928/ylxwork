import scrapy, pymysql, time
from gpcgd_gd_gov_cn.redis_conn import redis_conn
from gpcgd_gd_gov_cn.data_process import *
from gpcgd_gd_gov_cn.items import Item
from gpcgd_gd_gov_cn.settings import BOT_NAME

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'gpcgd.gd.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
           f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 32,
    }
    redis_name = '政府招标:' + host

    start_pages = [
        20, 20, 20, 2, 1, 3, 5
    ]
    def start_requests(self):
        for i in range(len(self.start_pages)):
            condition = True
            for page in range(self.start_pages[i]+1):
                start_urls = [
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/cgxxgg/index.html',  # 采购信息公告
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/zbjjgs/index.html',  # 中标、成交结果公告
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/cqgzgg/index.html',  # 澄清更正公告
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/cgxxyg/index.html',  # 采购信息预告
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/zgysgg/index.html',  # 资格预审公告
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/zbhxrgs/index.html',  # 中标候选人公示
                    'http://gpcgd.gd.gov.cn/bsfw/cgxx/pljzcgzl/index.html',  # 批量集中采购专栏
                ]
                if page < 1:
                    url = start_urls[i]
                else:
                    url = start_urls[i].replace('index', f'index_{str(page)}')

                query = get_link(url=url,rpath="//h3/a/@href")
                for item in query:
                    url = item

                    conn = redis_conn()
                    result = conn.find_data(value=url)
                    if result is False:
                        yield scrapy.Request(url=url, callback=self.con_parse)
                    else:
                        condition = False
                if condition is False:
                    break

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h1[@class='article_t']")
            date = result.dpath("//div[@class='article_item clearfix']", rule=None)
            content = result.xpath("//div[@class='article_con']", filter="script|style")

            file = result.fxpath("//div[@class='article_con']//a|/div[@class='article_con2']//a")
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
