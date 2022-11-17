# http://jsggzy.jszwfw.gov.cn/
# http://jsggzy.jszwfw.gov.cn/jyxx/tradeInfonew.html

import scrapy, pymysql, time
from jsggzy_jszwfw_gov_cn.redis_conn import redis_conn
from jsggzy_jszwfw_gov_cn.data_process import *
from jsggzy_jszwfw_gov_cn.items import Item
from jsggzy_jszwfw_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'jsggzy.jszwfw.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
             'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 32,
    }
    start_pages = [50, 18, 50]

    def start_requests(self):
        for i in range(3):
            num = 0
            condition = True
            for page in range(self.start_pages[i]+1):
                url = 'http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNew'
                data = [
                    # 采购公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"infodatepx\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"003004002"}],"time":[{"fieldName":"infodatepx","startTime":"2022-07-01 00:00:00","endTime":"%s 23:59:59"}],"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"isBusiness":"1"}'%(num, get_datetime_now()),
                    # 更正公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"infodatepx\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"003004003"}],"time":[{"fieldName":"infodatepx","startTime":"2022-07-01 00:00:00","endTime":"%s 23:59:59"}],"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"isBusiness":"1"}'%(num, get_datetime_now()),
                    # 成交公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"infodatepx\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"003004006"}],"time":[{"fieldName":"infodatepx","startTime":"2022-07-01 00:00:00","endTime":"%s 23:59:59"}],"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"isBusiness":"1"}'%(num, get_datetime_now()),

                ]
                body = data[i]
                num += 20

                data = post_link_json(url=url, data=body)
                records = data['result']['records']
                for data in records:
                    linkurl = 'http://jsggzy.jszwfw.gov.cn/' + data['linkurl']

                    conn = redis_conn()
                    result = conn.find_data(value=linkurl)
                    if result is False:
                        yield scrapy.Request(url=linkurl, callback=self.con_parse)
                    else:
                        print('已存在:', linkurl)
                    condition = False
                if condition is False:
                    break

    def con_parse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = result.xpath("//h2[@class='ewb-trade-h']")
            date = result.dpath("//div[@class='ewb-trade-info']", rule=None)
            content = result.xpath("//div[@class='ewb-trade-con clearfix']/div[@class='ewb-trade-right l']", filter=None)
            content_result = process_content_type(C=content)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = date
            item['contenttype'] = content_result
            item['doc_content'] = content
            # yield item
            print(item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
