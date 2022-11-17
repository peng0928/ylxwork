# area 广东省公共资源交易平台
# https://www.gdzwfw.gov.cn/ggzy/gdyzwzh/
import scrapy, pymysql, time
from ygp_gdzwfw_gov_cn.redis_conn import redis_conn
from ygp_gdzwfw_gov_cn.data_process import *
from ygp_gdzwfw_gov_cn.items import Item
from ygp_gdzwfw_gov_cn.settings import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ygp.gdzwfw.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
           f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3
        # 'CONCURRENT_REQUESTS': 32
    }
    headers = {
        'Content-Type': 'application/json',
        }

    def start_requests(self):
        start_url = 'https://ygp.gdzwfw.gov.cn/ggzy-portal/search/v1/items' # 交易广告
        for page in range(1, 9994):
            condition = True
            data1 = '{"type":"trading-type","publishStartTime":"","publishEndTime":"","siteCode":"44","secondType":"A","projectType":"","thirdType":"","dateType":"","pageNo":%s,"pageSize":10,"openConvert":true}'%page

            json_res = post_link_json(url=start_url, data=data1, headers=self.headers)['data']['pageData']
            for query in json_res:
                lurl = f'https://ygp.gdzwfw.gov.cn/ggzy-portal/center/apis/trading-notice/detail?tradingType=A&projectCode=' + \
                              query['projectCode'] + '&tradingProcess=A02&siteCode=440300'

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
            data = res.json()['data'][0]
            result = Xpath(data['noticeContent'])
            title = data['noticeName']
            date = data['noticeSendTime']
            content = result.xpath("", filter=None)
            file = result.fxpath("//td/a")
            filename = file[0]
            filelink = file[1]
            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filelink)

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
