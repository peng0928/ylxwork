# http://ggzy.xjbt.gov.cn/TPFront/
import scrapy, pymysql, time
from ggzy_xjbt_gov_cn.redis_conn import redis_conn
from ggzy_xjbt_gov_cn.data_process import *
from ggzy_xjbt_gov_cn.items import Item
from ggzy_xjbt_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzy.xjbt.gov.cn'
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


    start_urls= [
        # 工程建设-招标公告
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001002/?Paging=1',
        # 工程建设-答疑澄清
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001003/?Paging=1',
        # 工程建设-中标候选人公示
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001004/?Paging=1',
        # 工程建设-中标结果公告
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001005/?Paging=1',
        # 工程建设-资格预审公示
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001006/?Paging=1',
        # 工程建设-变更公告
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001007/?Paging=1',
        # 工程建设-定标候选人公示
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004001/004001008/?Paging=1',

        # 政府采购-单一来源公示
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004002/004002006/?Paging=1',
        # 政府采购-采购公告
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004002/004002002/?Paging=1',
        # 政府采购-变更公告
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004002/004002003/?Paging=1',
        # 政府采购-结果公示
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004002/004002005/?Paging=1',
        # 政府采购-合同公示
        'http://ggzy.xjbt.gov.cn/TPFront/jyxx/004002/004002007/?Paging=1',
    ]
    start_pages = [2390, 954, 1490, 1432, 2, 381, 1, 64, 1735, 344, 1775, 184]

    def start_requests(self):
        for i in range(12):
            condition = True
            for page in range(1, self.start_pages[i]+1):
                url = self.start_urls[0].replace('Paging=1', f'Paging={page}')
                query = get_link(url=url, rpath="//a[@class='WebList_sub']/@href")
                for item in query:
                    lurl = 'http://ggzy.xjbt.gov.cn' + item
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
            title = result.xpath("//td[@id='tdTitle']//b")
            date = result.dpath("//font[@class='webfont']", rule=None)
            content = result.xpath("//div[@class='infodetail']", filter='title|script|style')
            file = result.fxpath("//table[@id='filedown']//a")
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
