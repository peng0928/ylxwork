# http://zjpubservice.zjzwfw.gov.cn/jyxxgk/list.html
import scrapy, pymysql, time
from zjpubservice_zjzwfw_gov_cn.redis_conn import redis_conn
from zjpubservice_zjzwfw_gov_cn.data_process import *
from zjpubservice_zjzwfw_gov_cn.items import Item
from zjpubservice_zjzwfw_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'zjpubservice.zjzwfw.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 0.6,
        'CONCURRENT_REQUESTS': 32,
    }

    def start_requests(self):
        for i in range(4):
            page = 0
            condition = True
            for num in range(100):
                data = [
                    # 中标成交公告
                    '{"token":"","pn":%d,"rn":12,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"webdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"002002002"},{"fieldName":"infoc","isLike":true,"likeType":2,"equal":"33"}],"time":[{"fieldName":"webdate","startTime":"2022-5-12 00:00:00","endTime":"%s 23:59:59"}],"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"0","searchRange":null,"isBusiness":"1"}'%(page, get_datetime_now()),
                    # 更正公告
                    '{"token":"","pn":%d,"rn":12,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"webdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"002002003"},{"fieldName":"infoc","isLike":true,"likeType":2,"equal":"33"}],"time":[{"fieldName":"webdate","startTime":"2022-5-12 00:00:00","endTime":"%s 23:59:59"}],"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"0","searchRange":null,"isBusiness":"1"}'%(page, get_datetime_now()),
                    # 采购合同
                    '{"token":"","pn":%d,"rn":12,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"webdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"002002002"},{"fieldName":"infoc","isLike":true,"likeType":2,"equal":"33"}],"time":[{"fieldName":"webdate","startTime":"2022-5-12 00:00:00","endTime":"%s 23:59:59"}],"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"0","searchRange":null,"isBusiness":"1"}'%(page, get_datetime_now()),
                    # 废标公告
                    '{"token":"","pn":%d,"rn":12,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"webdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"002002007"},{"fieldName":"infoc","isLike":true,"likeType":2,"equal":"33"}],"time":[{"fieldName":"webdate","startTime":"2022-5-12 00:00:00","endTime":"%s 23:59:59"}],"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"0","searchRange":null,"isBusiness":"1"}'%(page, get_datetime_now()),

                ]
                page += 12
                body = data[i]
                url = 'http://zjpubservice.zjzwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData'
                query = post_link_json(url=url, data=body)['result']['records']
                for data in query:
                    lurl = 'http://zjpubservice.zjzwfw.gov.cn' + data['linkurl']
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
            title = result.xpath("//div[@class='article-info']/h1")
            date = result.dpath("//div[@class='article-info']/p[@class='info-sources']", rule=None)
            content = result.xpath("//div[@class='article-info']/div[@class='con']", filter="script|style")

            file = result.fxpath("//ul[@class='fjxx']//a")
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
            print(item)
            # yield item

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
