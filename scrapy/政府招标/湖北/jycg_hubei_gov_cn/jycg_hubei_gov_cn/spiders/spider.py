import scrapy
from redis_conn import redis_conn
from ..data_process import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'jycg.hubei.gov.cn'

    start_index = [223, 44, 262]
    # start_index = [2, 2, 2]
    condition = True
    def start_requests(self):
        for i in range(0,3):
            self.condition = True
            for page in range(1, self.start_index[i]):
                page = str(page)
                start_url = [
                    f'https://jycg.hubei.gov.cn/info-query/jycgnoticeinfo/list.do?pageIndex={page}&pageSize=12&type=2',
                    # 采购公告
                    f'http://jycg.hubei.gov.cn/info-query/jycgnoticeinfo/list.do?pageIndex={page}&pageSize=12&type=3',
                    # 变更公告
                    f'http://jycg.hubei.gov.cn/info-query/jycgnoticeinfo/list.do?pageIndex={page}page61&pageSize=12&type=4',
                    # 结果公告
                    ]
                url = start_url[i]
                if self.condition is True:
                    yield scrapy.Request(url=url, callback=self.dparse)
                else:
                    break

    def dparse(self, response):
        conn = redis_conn()
        data = response.json()['data']['records']
        for query in data:
            noticeid = query['noticeid']
            lurl = f'http://jycg.hubei.gov.cn/info-query/jycgnoticeinfo/detail.do?id={noticeid}&newdata=1'
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse)
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        print(response.text)
        cresult = response.json().get('data', None)
        item = {}
        if cresult:
            rxpath = Xpath(cresult.get('content', None))
            content = rxpath.xpath("//div[@class='Section1']", filter='script|style')
            if content is None:
                content = rxpath.xpath("", filter='script|style')

            title = cresult.get('title', None)
            pubtime = cresult.get('pubtime', None)
            pubtime = process_timestamp(pubtime)
            file = cresult.get('attaches', None)
            if not file:
                filename = ''
                filelink = ''
            else:
                filename = file[0].get('name', None)
                attachid = file[0].get('attachid', None)
                noticeid = file[0].get('noticeid', None)
                filelink = f'http://jycg.hubei.gov.cn/info-query/jycg/downloadfile.do?attachid={attachid}&newdata=1&noticeid={noticeid}'

            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filelink)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = pubtime
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            # yield item
            print(item)



