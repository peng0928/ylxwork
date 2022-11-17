# 网站地址 http://ggzyjy.gansu.gov.cn/

import scrapy, pymysql, time, re
from ggzyjy_gansu_gov_cn.redis_conn import redis_conn
from ggzyjy_gansu_gov_cn.data_process import *
from ggzyjy_gansu_gov_cn.items import Item
from ggzyjy_gansu_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'pzxx.ggzyjy.gansu.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    condition = True
    def start_requests(self):
        url = 'https://pzxx.ggzyjy.gansu.gov.cn/f/newprovince/annogoods/getAnnoList'
        for page in range(1, 4275):
            data = f'pageNo={page}&pageSize=10&area=620000&prjpropertynewI=I&prjpropertynewA=A&prjpropertynewD=D&prjpropertynewC=C&prjpropertynewB=B&prjpropertynewE=E&projectname='
            if self.condition is True:
                yield scrapy.Request(url=url, method='POST', headers=self.headers, body=data, callback=self.lparse)
                time.sleep(3)
            else:
                break

    def lparse(self, response):
        conn = redis_conn()
        title = response.xpath("//dd[@class='clear']//a//text()").getall()
        query = response.xpath("//dd[@class='clear']//a/@onclick").getall()
        date = response.xpath("///dd[@class='clear']/i//text()").getall()
        for item in range(len(query)):
            url = 'https://pzxx.ggzyjy.gansu.gov.cn' + query[item]
            pbdate = date[item]
            pbtitle = title[item]
            id = re.findall('\(\'(\d+)\',', url)[0]
            id = f'bidpackages=&tenderprojectid={id}&index=0&area=620000'
            lurl = 'https://pzxx.ggzyjy.gansu.gov.cn/f/newprovince/tenderproject/flowpage'
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse, body=id, headers=self.headers, method='POST',
                                     meta={'pbdate': pbdate, "pbtitle": pbtitle, "url": lurl + '?' + id})
                time.sleep(5)
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        item = {}
        result = Xpath(response.text)
        title = process_text(response.meta['pbtitle'])
        date = response.meta['pbdate']
        content = result.xpath("", filter="script|style")
        content_result = process_content_type(C=content)
        item['host'] = self.host
        item['pageurl'] = response.meta['url']
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = content
        item['contenttype'] = content_result
        # print(item)
        yield item

