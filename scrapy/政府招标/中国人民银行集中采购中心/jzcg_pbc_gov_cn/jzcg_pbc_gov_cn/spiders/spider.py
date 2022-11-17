import scrapy, requests
from scrapy import cmdline
from jzcg_pbc_gov_cn.data_process import *
from lxml import etree
from jzcg_pbc_gov_cn.items import Item
from jzcg_pbc_gov_cn.redis_conn import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'LOG_LEVEL': 'INFO'
    }
    pageindex = [8, 5]
    start_urls = [
        # 总行采购公告
        'https://jzcg.pbc.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=9e9a312c-e98f-4516-95ff-74af73e2f6c4&channel=4081b14c-c0a5-4585-ae0f-60c72b29beb0&noticeType=&currPage=&pageSize=10&operationStartTime=&operationEndTime=&title=&purchaseManner=&agency=%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E9%93%B6%E8%A1%8C%E9%9B%86%E4%B8%AD%E9%87%87%E8%B4%AD%E4%B8%AD%E5%BF%83&selectTimeName=noticeTime',
        # 分支机构及直属单位公告
        'https://jzcg.pbc.gov.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=9e9a312c-e98f-4516-95ff-74af73e2f6c4&channel=4081b14c-c0a5-4585-ae0f-60c72b29beb0&noticeType=&currPage=&pageSize=10&operationStartTime=&operationEndTime=&title=&purchaseManner=&agency=!%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E9%93%B6%E8%A1%8C%E9%9B%86%E4%B8%AD%E9%87%87%E8%B4%AD%E4%B8%AD%E5%BF%83&selectTimeName=noticeTime',
    ]
    host = 'jzcg.pbc.gov.cn'
    def start_requests(self):
        for i in range(2):
            condition = True
            for page in range(1, self.pageindex[i]+1):
                url = self.start_urls[i].replace('currPage=', f'currPage={page}')
                res = requests.get(url=url)
                data = res.json()['data']

                for query in data:
                    htmlpath = query['htmlpath']
                    htmlurl = 'https://jzcg.pbc.gov.cn/freecms' + htmlpath
                    conn = redis_conn()
                    result = conn.find_data(value=htmlurl)
                    if result is False:
                        yield scrapy.Request(url=htmlurl, callback=self.cparse)
                    else:
                        print('已存在:',htmlurl)
                        condition = False

                if condition is False:
                    break


    def cparse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h1[@class='info-title']")
            date = result.dpath("//span[@id='noticeTime']", rule=None)
            content = result.xpath("//div[@id='content']", filter="script|style")
            content_result = process_content_type(C=content)
            filename = response.xpath("//div[@id='content']//a//text()").extract() or None
            filelink = response.xpath("//div[@id='content']//a/@href").extract() or None
            if filelink is not None and filename is not None:
                fileurl = ''
                filename = '|'.join(filename)
                filelink = fileurl + f'|{fileurl}'.join(filelink)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            item['filename'] = filename
            item['filelink'] = filelink
            yield item
            # print(item)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
