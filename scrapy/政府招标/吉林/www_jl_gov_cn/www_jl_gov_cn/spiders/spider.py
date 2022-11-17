# http://www.jl.gov.cn/ggzy/
# http://www.jl.gov.cn/ggzy/zfcg/cggg/
import scrapy, pymysql, time, json
from ..redis_conn import redis_conn
from ..data_process import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.jl.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            # f'www_jl_gov_cn.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        # 'LOG_LEVEL': 'INFO',
        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1
    }
    condition = True
    def start_requests(self):
        for page in range(1, 14184):
            url = f'http://was.jl.gov.cn/was5/web/search?channelid=237687&page={page}&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD%27%20%20%20'
            if self.condition is True:
                yield scrapy.Request(url=url, callback=self.lparse)
                time.sleep(5)
            else:
                break

    def lparse(self, response):
        # conn = redis_conn()
        result = response.text.replace('result(', '')[:-4]
        result_json = json.loads(result).get('datas', None)
        for query in result_json:
            lurl = query.get('docpuburl', None)
            # result = conn.find_data(value=lurl)
            # if result is False:
            yield scrapy.Request(url=lurl, callback=self.cparse)
            time.sleep(5)
            # else:
            #     print('已存在:', lurl)
                #self.condition = False

    def cparse(self, response):
        item = {}
        result = Xpath(response.text)
        title = result.xpath("//h3[@class='ewb-article-tt']")
        date = result.dpath("//div[@class='ewb-article-sources']", rule=None)
        content = result.xpath("//div[@class='ewb-article-info']", filter="script|style")

        file = result.fxpath("//div[@class='ewb-article-info']//a")
        filename = file[0]
        filelink = file[1]

        item['filename'] = filename
        item['filelink'] = filelink
        content_result = process_content_type(C=content, F=filelink)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = response.text
        item['contenttype'] = content_result
        # yield item
        print(item)

