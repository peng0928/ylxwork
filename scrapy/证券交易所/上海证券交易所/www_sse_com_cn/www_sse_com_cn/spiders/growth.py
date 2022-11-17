import scrapy, requests
from urllib.parse import urljoin
from datetime import date, timedelta
from www_szse_cn.items import Item
from www_szse_cn.redis_conn import *

class SpiderSpider(scrapy.Spider):
    name = 'growth'
    duplicates = True

    def start_requests(self):
        today = (date.today() + timedelta(days=-0)).strftime("%Y-%m-%d")
        yesterday = (date.today() + timedelta(days=-27)).strftime("%Y-%m-%d")
        url = [f'http://query.sse.com.cn/security/stock/queryCompanyBulletin.do?isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=3&productId=&securityType=120100%2C020100%2C020200%2C120200&reportType2=DQBG&reportType=ALL&beginDate={yesterday}&endDate={today}']
        headers = {'Referer': 'http://www.sse.com.cn/'}
        total = requests.get(url=url[0], headers=headers).json()['pageHelp']['total']//25
        for page in range(1, total+2):
            print(page, '==============')
            lurl = url[0].replace('pageNo=1', f'pageNo={page}').replace('beginPage=1', f'beginPage={page}')
            if self.duplicates is True:
                yield scrapy.Request(url=lurl, callback=self.lparse, headers=headers)

            else:
                print('结束啦')
                break
    def lparse(self, response):
        item = Item()
        conn = redis_conn()
        jesult = response.json()['result']
        for query in jesult:
            TITLE = query['TITLE']
            URL = query['URL']
            fileName = ''.join(URL.split('/'))
            PDF = urljoin('http://www.sse.com.cn', URL)
            SSEDATE = query['SSEDATE']
            SECURITY_NAME = query['SECURITY_NAME']
            SECURITY_CODE = query['SECURITY_CODE']

            item['companyCd'] = SECURITY_CODE
            item['companyName'] = SECURITY_NAME
            item['destFilePath'] = PDF
            item['publishDate'] = SSEDATE
            item['disclosureTitle'] = TITLE
            item['fileName'] = fileName
            item['status'] = 0
            item['stockName'] = '2'
            result = conn.find_data(value=PDF)
            if result is False:
                yield item
                # print(item)
            else:
                self.duplicates = False
                print('已存在', PDF)



############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
