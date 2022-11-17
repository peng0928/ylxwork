import scrapy, pymysql, time, requests
from zw_hainan_gov_cn.redis_conn import redis_conn
from zw_hainan_gov_cn.data_process import *
from zw_hainan_gov_cn.items import Item
from zw_hainan_gov_cn.settings import *
from lxml import etree


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'zw.hainan.gov.cn'

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
    'DOWNLOAD_DELAY': 3
    # 'CONCURRENT_REQUESTS': 32
}

    start_pages  = [2080, 2671, 343, 2501, 2431, 439]
    start_urls  = [
        'https://zw.hainan.gov.cn/ggzy/ggzy/jgzbgg/index.jhtml', # 建设工程-招标公告
        'http://zw.hainan.gov.cn/ggzy/ggzy/jgzbgs/index.jhtml', # 建设工程-中标公示
        'http://zw.hainan.gov.cn/ggzy/ggzy/jsqtgg/index.jhtml', # 建设工程-其它公告
        'http://zw.hainan.gov.cn/ggzy/ggzy/cggg/index.jhtml', # 政府采购-采购公告
        'http://zw.hainan.gov.cn/ggzy/ggzy/cgzbgg/index.jhtml', # 政府采购-中标公告
        'http://zw.hainan.gov.cn/ggzy/ggzy/zfcgqtgg/index.jhtml', # 政府采购-其它公告
    ]

    def start_requests(self):
        for i in range(6):
            condition = True
            for page in range(1, self.start_pages[i]+1):
                url = self.start_urls[i].replace('index', f'index_{page}')
                query = requests.get(url)
                query = etree.HTML(query.text)
                link = query.xpath("//table[@class='newtable']//td/a/@href")
                date = query.xpath("//table[@class='newtable']/tbody/tr/td[4]//text()")
                for item in range(len(link)):
                    lurl = link[item]
                    pubdate = date[item]
                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse, meta={'pubdate': pubdate})
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break

    def con_parse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = result.xpath("//div[@class='newsTex']/h1")
            content = result.xpath("//div[@class='newsTex']/div[@class='newsCon']", filter='style|script')
            content_result = process_content_type(C=content)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = res.meta['pubdate']
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
