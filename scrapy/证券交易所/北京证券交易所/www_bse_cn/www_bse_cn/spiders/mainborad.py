import scrapy, json
from www_bse_cn.items import Item
from www_bse_cn.redis_conn import *
from urllib.parse import urljoin

class SpiderSpider(scrapy.Spider):
    name = 'bsespider'
    start_urls = ['http://www.bse.cn/disclosureInfoController/infoResult_zh.do']
    duplicates = True

    def start_requests(self):
        lurl = self.start_urls[0]
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.bse.cn/disclosure/announcement.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }
        for page in range(36):
            data = f'siteId=6&flag=0&page={page}&companyCd=&isNewThree=1&keyword=&xxfcbj%5B%5D=2&needFields%5B%5D=companyCd&needFields%5B%5D=companyName&needFields%5B%5D=disclosureTitle&needFields%5B%5D=disclosurePostTitle&needFields%5B%5D=destFilePath&needFields%5B%5D=publishDate&needFields%5B%5D=xxfcbj&needFields%5B%5D=destFilePath&needFields%5B%5D=fileExt&needFields%5B%5D=xxzrlx&sortfield=xxssdq&sorttype=asc'
            if self.duplicates is True:
                yield scrapy.Request(url=lurl, method='POST', headers=headers, body=data, callback=self.lparse)
            else:
                print('结束啦')
                break

    def lparse(self, response):
        jsult = json.loads(response.text[6:-2])['listInfo']['content']
        item = Item()
        conn = redis_conn()
        for query in jsult:
            companyCd = query['companyCd']
            companyName = query['companyName']
            destFile =''.join(query['destFilePath'].split('/'))
            destFilePath = urljoin('http://www.bse.cn',query['destFilePath'])
            disclosureTitle = query['disclosureTitle']
            publishDate = query['publishDate']

            item['companyCd'] = companyCd
            item['companyName'] = companyName
            item['destFilePath'] = destFilePath
            item['publishDate'] = publishDate
            item['disclosureTitle'] = disclosureTitle
            item['fileName'] = destFile
            item['status'] = 0
            item['stockName'] = '6'

            result = conn.find_data(value=destFilePath)
            if result is False:
                yield item
                # print(item)
            else:
                self.duplicates = False
                print('已存在', destFilePath)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
