import scrapy, json, re
from scrapy import cmdline
from www_szse_cn.settings import *
from www_szse_cn.items import Item
from www_szse_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider1'
    start_opt = {
        'url': 'https://www.szse.cn/api/disc/announcement/annList',
        'data': {"seDate": ["", ""], "plateCode": ["16"], "channelCode": ["fixed_disc"], "pageSize": 50, "pageNum": 4},
        'headers': {'Content-Type': 'application/json'},
        'duplicates': True
    }

    def start_requests(self):
        url = self.start_opt['url']
        headers = self.start_opt['headers']
        for page in range(1, 501):
            duplicates = self.start_opt['duplicates']
            print('===============', page)
            if duplicates is True:
                self.start_opt['data']['pageNum'] = page
                data = json.dumps(self.start_opt['data'])
                yield scrapy.Request(url=url, body=data, headers=headers, method='POST',
                                     callback=self.cparse, meta={'page': page})
            else:
                print('结束啦')
                break

    def cparse(self, response):
        data = response.json()['data']
        item = Item()
        conn = redis_conn()
        for query in data:
            title = query.get('title', None)
            publishTime = query.get('publishTime', None)
            publishTime = re.findall('(\d{4}-\d{1,2}-\d{1,2})', publishTime)[0]
            attachPath = 'https://disc.szse.cn/download' + query.get('attachPath', None)
            fileName = ''.join(query.get('attachPath', None).split('/')).replace('-', '')
            secCode = query.get('secCode', None)[0]
            secName = query.get('secName', None)[0]

            item['companyCd'] = secCode
            item['companyName'] = secName
            item['destFilePath'] = attachPath
            item['publishDate'] = publishTime
            item['disclosureTitle'] = title
            item['fileName'] = fileName
            item['status'] = 0
            item['stockName'] = '5'
            result = conn.find_data(value=attachPath)
            if result is False:
                yield item
                # print(item)
            else:
                self.start_opt['duplicates'] = False
                print('已存在', response.meta['page'])


if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
