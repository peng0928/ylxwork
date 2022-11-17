# http://ccgp-jiangxi.gov.cn/web/
import scrapy, pymysql, time, json
from ccgp_jiangxi_gov_cn.redis_conn import redis_conn
from ccgp_jiangxi_gov_cn.data_process import *
from ccgp_jiangxi_gov_cn.items import Item
from ccgp_jiangxi_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ccgp-jiangxi.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
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

    condition = True
    def start_requests(self):
        for page in range(1, 12580):
            # url = [
            #     # 采购公告
            #     f'http://ccgp-jiangxi.gov.cn/web/jyxx/002006/002006001/{page}.html',
            #     # 变更公告
            #     f'http://ccgp-jiangxi.gov.cn/web/jyxx/002006/002006002/{page}.html',
            #     # 结果公示
            #     f'http://ccgp-jiangxi.gov.cn/web/jyxx/002006/002006004/{page}.html',
            # ]
            url = f'http://ccgp-jiangxi.gov.cn/jxzfcg/services/JyxxWebservice/getList?response=application/json&pageIndex={page}&pageSize=22&area=&prepostDate={get_datetime_now(reduce_months=6)}&nxtpostDate={get_datetime_now()}&xxTitle=&categorynum=002006'

            if self.condition is True:
                yield scrapy.Request(url=url, callback=self.lparse)
            else:
                print('已存在:', url)
                break

    def lparse(self, response):
        response_json = response.json()['return']
        response_json = json.loads(response_json)
        Table = response_json['Table']
        conn = redis_conn()
        for i in Table:
            infoid = i['infoid']
            postdate = i['postdate'].replace('-', '')
            categorynum1 = i['categorynum']
            categorynum2 = categorynum1[:-3]

            lurl = f'http://ccgp-jiangxi.gov.cn/web/jyxx/{categorynum2}/{categorynum1}/{postdate}/{infoid}.html'
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.con_parse)
            else:
                print('已存在:', lurl)
                self.condition = False

    def con_parse(self, res):
        item = {}

        result = Xpath(res.text)
        title = result.xpath("//div[@class='article-info']/h1")
        date = result.dpath("//p[@class='infotime']|//p[@class='info-sources']", rule=None)
        content = result.xpath("//div[@class='article-info']/div[@class='con']",
                               filter="ul[@class='fjxx']|p[@class='fjxx']|style|script")
        content_result = process_content_type(C=content)

        file = result.fxpath("//div[@class='con attach']/a", rule='http://ccgp-jiangxi.gov.cn')
        filename = file[0]
        filelink = file[1]

        item['filename'] = filename
        item['filelink'] = filelink
        item['host'] = self.host
        item['pageurl'] = res.url
        item['docsubtitle'] = title
        item['publishdate'] = date
        item['contenttype'] = content_result
        item['pagesource'] = res.text
        yield item
        # print(item)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
