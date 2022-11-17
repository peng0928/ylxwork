# http://www.ccgp-xizang.gov.cn/freecms/site/xizang/xzcggg/index.html
import scrapy, pymysql, time
from www_ccgp_xizang_gov_cn.redis_conn import redis_conn
from www_ccgp_xizang_gov_cn.data_process import *
from www_ccgp_xizang_gov_cn.items import Item
from www_ccgp_xizang_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-xizang.gov.cn'
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

    def start_requests(self):
        for page in range(1, 194):
            condition = True
            url = f'http://www.ccgp-xizang.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=18de62f0-2fb0-4187-a6c1-cd8fcbfb4585&channel=b541ffff-03ee-4160-be64-b11ccf79660d&currPage={page}&pageSize=100&noticeType=%&cityOrArea=&noticeName=&operationStartTime=&operationEndTime=&selectTimeName=noticeTime'
            query = get_link_json(url)

            query = query['data']
            for data in query:
                lurl = 'http://www.ccgp-xizang.gov.cn' + data['pageurl']
                f_noticeTime = data['fieldValues']['f_noticeTime']

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.con_parse, meta={'f_noticeTime': f_noticeTime})
                else:
                    print('已存在:', lurl)
                    condition = False
                time.sleep(5)
            if condition is False:
                break

    def con_parse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = result.xpath("//div[@class='notice-hear']/h2")
            date = res.meta['f_noticeTime']
            content = result.xpath("//div[@id='print-content']/div[@class='notice-con']", filter='script|style')
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
