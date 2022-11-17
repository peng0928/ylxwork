import scrapy, pymysql, time
from www_ccgp_hainan_gov_cn.redis_conn import redis_conn
from www_ccgp_hainan_gov_cn.data_process import *
from www_ccgp_hainan_gov_cn.items import Item
from www_ccgp_hainan_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-hainan.gov.cn'
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

    def start_requests(self):
        for page in range(1,7197):
            condition = True
            url = f'https://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?currentPage={page}'
            query = get_link(url, "//div[starts-with(@class,'index')]//li//a/@href")
            for item in query:
                lurl = 'https://www.ccgp-hainan.gov.cn' + item
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
            title = result.xpath("//div[@class='zx-xxxqy']/h2")
            date = result.dpath("//div[@class='ty-p1']", rule=None)
            content = result.xpath("//div[@class='xly']/div[@class='content01']", filter="style|script|div[@class='content04']|div[@class='content_1_2']")
            file = result.fxpath("//div[@class='content01']/div[@id='con_TBAB_1']/a", rule='https://www.ccgp-hainan.gov.cn')
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
