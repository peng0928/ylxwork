import scrapy, pymysql, time
from ggzy_guiyang_gov_cn.redis_conn import redis_conn
from ggzy_guiyang_gov_cn.data_process import *
from ggzy_guiyang_gov_cn.items import Item
from ggzy_guiyang_gov_cn.settings import BOT_NAME


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzy.guiyang.gov.cn'
    custom_settings = {
        'redis_name': '政府招标:ggzy.guiyang.gov.cn',
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
    start_pages = [
        453, 100, 4, 565, 106
    ]
    def start_requests(self):
        for i in range(5):
            condition = True
            for page in range(self.start_pages[i]):
                start_urls = [
                    'http://ggzy.guiyang.gov.cn/zfcg/zbgg_5372418/hw/index.html',  # 采购公告
                    'http://ggzy.guiyang.gov.cn/zfcg/bgcqgg/hw_5372423/index.html',  # 更正公告
                    'http://ggzy.guiyang.gov.cn/zfcg/zzgg/hw_5372427/index.html',  # 终止公告
                    'http://ggzy.guiyang.gov.cn/zfcg/zbcjjggg/hw_5372435/index.html',  # 中标（成交）结果公告
                    'http://ggzy.guiyang.gov.cn/zfcg/fbgg/hw_5372439/index.html',  # 废标公告
                ]
                if page < 1:
                    url = start_urls[i]
                else:
                    url = start_urls[i].replace('index', f'index_{str(page)}')

                query = get_link(url,"//div[@id='conList']//a/@href")
                for lurl in query:
                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break

    def con_parse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = result.xpath("//div[@class='wzy_title']")
            date = result.dpath("//div[@class='time fl']", rule='发布日期：')
            content = result.xpath("//div[@id='zoom']", filter="a[@class='fl']|style|script")
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
