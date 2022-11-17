import scrapy, requests
from scrapy import cmdline
from www_zycg_gov_cn.items import Item
from www_zycg_gov_cn.pymysql_connection import pymysql_connection
from www_zycg_gov_cn.data_process import *
from www_zycg_gov_cn.redis_conn import *

class SpiderSpider(scrapy.Spider):
    name = 'zycggovspider'
    custom_settings = {
        'LOG_LEVEL': 'WARNING',
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {
            'www_zycg_gov_cn.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Cookie': 'JSESSIONID=D28E883232786DDFDF8B823359BE668E; jfe_pin=043a9b1b; jfe_ts=1658724219.85; jfe_sn=hiRokZ3/Ym2bV0uPXFXNYA7DJNE=; VFSESS=jsc128269924+HkMrmc4U=',
            'Host': 'www.zycg.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        },
    }
    host = 'www.zycg.gov.cn'

    def start_requests(self):
        conn = redis_conn()
        for page in range(1, 2819):
            condition = True
            url = f'https://www.zycg.gov.cn/freecms/rest/v1/notice/selectInfoMore.do?&siteId=6f5243ee-d4d9-4b69-abbd-1e40576ccd7d&channel=d0e7c5f4-b93e-4478-b7fe-61110bb47fd5&currPage={page}&pageSize=12&noticeType=1,2,3,31,32,57,52,61&implementWay=1&operationStartTime=&title=&operationEndTime='
            resp = requests.get(url=url, headers=self.custom_settings['DEFAULT_REQUEST_HEADERS']).json()
            data = resp['data']
            for i in data:
                pageurl = 'https://' + self.host + i['pageurl']
                id = i['id']
                meta = {
                    'id': id,
                }
                result = conn.find_data(value=pageurl)
                if result is False:
                    yield scrapy.Request(url=pageurl, callback=self.con_parse, meta=meta)
                else:
                    condition = False
            if condition is False:
                break

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h4[@class='info-title']")
            date = result.dpath("//div[@class='info-content']//time", rule=None)
            content = result.xpath("//div[@class='info-content']/div[@id='printArea']", filter="div[@class='change']|script|style")
            content_result = process_content_type(C=content)

            # link = 'https://www.zycg.gov.cn/freecms/rest/v1/notice/selectNoticeDocInfo.do?currPage=1&pageSize=10&id=%s'%response.meta["id"]
            # print(link)
            # resp = requests.get(headers=self.custom_settings['DEFAULT_REQUEST_HEADERS'], url=link).json()['data']
            # print(resp)
            # try:
            #     filename = resp['fileName'] or None
            #     filelink = resp['fileUrl'] or None
            #     if filelink is not None and filename is not None:
            #         fileurl = ''
            #         filename = '|'.join(filename)
            #         filelink = fileurl + f'|{fileurl}'.join(filelink)
            # except:
            #     filename = None
            #     filelink = None

            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            # item['filename'] = filename
            # item['filelink'] = filelink
            yield item
            # print(item)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    cmdline.execute(f"scrapy crawl {SpiderSpider.name}".split())
