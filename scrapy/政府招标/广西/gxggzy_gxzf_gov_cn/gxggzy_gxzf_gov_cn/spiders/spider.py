import scrapy, pymysql, time
from gxggzy_gxzf_gov_cn.redis_conn import redis_conn
from gxggzy_gxzf_gov_cn.data_process import *
from gxggzy_gxzf_gov_cn.items import Item
from gxggzy_gxzf_gov_cn.settings import BOT_NAME


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'gxggzy.gxzf.gov.cn'
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
        # 'DOWNLOAD_DELAY': 0.6
        # 'CONCURRENT_REQUESTS': 32
    }

    def start_requests(self):
        start_urls = [
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_gcjs/index.shtml',  # 工程建设
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_gcjs/index_1.shtml',  # 工程建设
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_zfcg/index.shtml',  # 政府采购
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_zfcg/index_1.shtml',  # 政府采购
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_yphylqxcg/index.shtml',  # 药品和医疗器械采购
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_yphylqxcg/index_1.shtml',  # 药品和医疗器械采购
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_qtjy/index.shtml',  # 其他交易
            'http://gxggzy.gxzf.gov.cn/jysj/jysj_sjfb/jysj_qtjy/index_1.shtml',  # 其他交易
        ]
        for query in start_urls:
            url = query

            query = get_link(url, "//div[@class='clearfix ewb-dynamics-wrap']/a/@href")
            for item in query:
                link = '/'.join(url.split('/')[:-1])
                lurl = link + item[1:]

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.con_parse)
                else:
                    print('已存在:', lurl)


    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h1[@class='h-title']")
            date = result.dpath("//div[@class='ewb-details-sub']", rule=None)
            content = result.xpath("//div[@class='ewb-page-line']", filter="h1[@class='h-title']|div[@class='ewb-details-sub']|p[@class='article-file bold']|script|style")

            # file = result.fxpath("")
            # filename = file[0]
            # filelink = file[1]
            #
            # item['filename'] = filename
            # item['filelink'] = filelink
            content_result = process_content_type(C=content,)
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
