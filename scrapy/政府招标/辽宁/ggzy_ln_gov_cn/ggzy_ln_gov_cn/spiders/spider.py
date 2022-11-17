# http://www.ccgp-jilin.gov.cn/
import scrapy, pymysql, time
from ggzy_ln_gov_cn.redis_conn import redis_conn
from ggzy_ln_gov_cn.data_process import *
from ggzy_ln_gov_cn.items import Item
from ggzy_ln_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzy.ln.gov.cn'
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
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 32,
    }

    start_urls = [
        # 采购公告
        'http://ggzy.ln.gov.cn/jyfb/zfcg/cggg/index.html',
        # 更正公告
        'http://ggzy.ln.gov.cn/jyfb/zfcg/cggg_153368/index.html',
        # 结果公告
        'http://ggzy.ln.gov.cn/jyfb/zfcg/jggg1/index.html',
    ]
    start_pages = [243, 62, 235]
    ############读取redis数据库爬取############
    def start_requests(self):
        for i in range(3):
            condition = True
            for page in range(self.start_pages[i]+1):
                if page > 0:
                    url = self.start_urls[i].replace('index', f'index_{page}')
                else:
                    url = self.start_urls[i]

                data = get_link(url, "//div[@class='dh_dright']//a/@href")
                for query in data:
                    lurl = '/'.join(url.split('/')[:-1]) + query[1:]

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
            title = result.xpath("//div[@class='dlist_title']")
            date = result.dpath("//div[@class='dlist_time']", rule=None)
            content = result.xpath("//div[@id='Zoom']", filter='style')

            file = result.fxpath("//div[@id='Zoom']/a")
            filename = file[0]
            filelink = file[1]

            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=None)
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
