import scrapy, time
from ..data_process import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    condition = True
    host = 'ggzy.hebei.gov.cn'

    def start_requests(self):
        url = 'http://ggzy.hebei.gov.cn/inteligentsearchfw/rest/inteligentSearch/getFullTextData'
        for i in range(50000, 50001):
            data = '{"token":"","pn":%d,"rn":10,"sdt":"","edt":"","wd":" ","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\\"webdate\\":0}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","equal":"003001001","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"0","searchRange":null,"isBusiness":"1"}'%(i*10)
            if self.condition is True:
                yield scrapy.Request(url=url, body=data, method='POST', headers=self.headers, callback=self.lparse)
                time.sleep(3)
            else:
                break

    def lparse(self, response):
        records = response.json().get('result', None).get('records', None)
        if records is not None:
            for query in records:
                linkurl = 'http://ggzy.hebei.gov.cn/hbggfwpt' + query.get('linkurl', None)
                webdate = query.get('webdate', None)
                yield scrapy.Request(url=linkurl, callback=self.cparse, meta={'webdate': webdate})
                time.sleep(3)
        else:
            print('*****lparse为空 列表json为空*****')

    def cparse(self, response):
        item = {}
        result = Xpath(response.text)
        title = result.xpath("//h2[@id='titlecontent']")
        date = response.meta['webdate']
        content = result.xpath("//div[@class='ewb-bulid-panel']/div[@class='ewb-copy']", filter="script|style")

        content_result = process_content_type(C=content)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = content
        item['contenttype'] = content_result
        # yield item
        print(item)