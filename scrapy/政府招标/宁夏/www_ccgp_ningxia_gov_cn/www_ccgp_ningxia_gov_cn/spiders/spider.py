# http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/index.jsp?id=1
import scrapy, pymysql, time
from www_ccgp_ningxia_gov_cn.redis_conn import redis_conn
from www_ccgp_ningxia_gov_cn.data_process import *
from www_ccgp_ningxia_gov_cn.items import Item
from www_ccgp_ningxia_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-ningxia.gov.cn'
    redis_name = '政府招标:' + host
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        # 'DOWNLOAD_DELAY': 0.6,
        # 'CONCURRENT_REQUESTS': 32,
    }


    def start_requests(self):
        for page in range(1,3):
            url = 'http://www.ccgp-ningxia.gov.cn/public/ZFGMFW/dynamic/contents/ZDXML/index.jsp?cid=2043&sid=2000'
            data = 'page=%s&title=&fbsj1=&fbsj2=' %page
            yield scrapy.Request(url=url, method='POST', body=data, callback=self.lparse)

    def lparse(self, res):
        query = res.xpath("//table[@class='newsTable listdt']//a/@href").extract()
        date = res.xpath("//table[@class='newsTable listdt']//th//text()").extract()
        title = res.xpath("//table[@class='newsTable listdt']//a//text()").extract()
        for i in range(len(query)):
            url = 'http://www.ccgp-ningxia.gov.cn/public/ZFGMFW/dynamic/' + query[i]
            time = date[i]
            tit = title[i]
            yield scrapy.Request(url=url, callback=self.cparse, meta={'date':time,'title':tit})

    def cparse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = res.meta['title']
            date = res.meta['date']
            content = result.xpath("//div[@class='con-page']", filter='style')
            content_result = process_content_type(C=content)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = date
            item['contenttype'] = content_result
            item['doc_content'] = content
            yield item
            # print(item)

        except Exception as e:
            print(e)




############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
