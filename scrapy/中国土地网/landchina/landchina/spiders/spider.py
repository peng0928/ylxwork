import math, json, uuid
import scrapy
from ..data_process import *
from ..decorator_penr import *


class SpiderSpider(scrapy.Spider):
    """中国土地市场网"""
    name = "spider"
    starturl = "https://api.landchina.com/tGyggZd/transfer/list"
    headers = {'Content-Type': 'application/json'}
    start_time = "2022-01-01 00:00:00"
    end_time = f"{get_datetime_now()} 23:59:59"
    req_data = '{"pageNum": 1, "pageSize": 10, "tdYt": "07", "startDate": "%s", "endDate": "%s"}' % (
    start_time, end_time)

    def start_requests(self):
        ii = int(input(':'))
        for i in range(ii, 2154):
            data = self.req_data.replace('pageNum": 1', f'pageNum": {i}')
            print(data)
            yield scrapy.Request(url=self.starturl, method='POST', headers=self.headers, body=data, meta={"page": i},
                                 callback=self.lparse)

    def get_page(self, response):
        obj = response.json()
        data = obj.get('data')
        if data:
            total = data.get('total')
            page = math.ceil(total / 10)  # 2022-01-01到至今
            print(page)
            for i in range(1500, page + 1):
                data = self.req_data.replace('pageNum": 1', f'pageNum": {i}')
                yield scrapy.Request(url=self.starturl, method='POST', headers=self.headers, dont_filter=True,
                                     body=data, callback=self.lparse, meta={"page": i})


    def lparse(self, response):
        print('当前页: ', response.meta['page'])
        item = {}
        obj = response.json()
        data = obj.get('data')
        total = data.get('total')
        if total < 30000:
            print(data)
            if data:
                list = data.get('list')
                for i in list:
                    xzqFullName = i.get('xzqFullName')  # 行政区
                    zdh = i.get('zdBh')  # 宗地编号
                    zdZl = i.get('zdZl')  # 土地坐落
                    mj = i.get('mj')  # 总面积(平方米)
                    tdYt = i.get('tdYt')  # 土地用途
                    gyFs = i.get('gyFs')  # 供应方式
                    fbSj = i.get('fbSj')  # 发布时间

                    item['xzqFullName'] = xzqFullName
                    item['zdh'] = zdh
                    item['zdZl'] = zdZl
                    item['mj'] = mj
                    item['tdYt'] = tdYt
                    item['gyFs'] = gyFs
                    item['fbSj'] = fbSj.replace('T', ' ')

                    uuid_str = str(item)
                    item_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, uuid_str)
                    item['uuid'] = str(item_uuid.hex)
                    # print(item)
                    yield item
        else:
            print('error')
            time.sleep(40)
            with open('./1.txt', 'a')as f:
                f.write(str(response.meta['page']) + '\n')



