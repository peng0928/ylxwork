import scrapy
from scrapy import cmdline
from lxml import etree
from hgcg_customs_gov_cn.data_process import *
from hgcg_customs_gov_cn.items import Item
from hgcg_customs_gov_cn.redis_conn import *
from fake_useragent import UserAgent

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        # 'LOG_LEVEL': 'WARNING'
    }
    host = 'hgcg.customs.gov.cn'
    start_urls = [
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=1&pageSize=25&total=0&columnId=8486928f23784ddfb055b8f9da46f285&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=1&pageSize=25&total=17&columnId=af8b307d33da4a69ad8224c806e38a80&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=2&pageSize=25&total=17&columnId=af8b307d33da4a69ad8224c806e38a80&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=3&pageSize=25&total=17&columnId=af8b307d33da4a69ad8224c806e38a80&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=1&pageSize=25&total=57&columnId=e2614343939f4c91907bd5a37c3d538d&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=2&pageSize=25&total=57&columnId=e2614343939f4c91907bd5a37c3d538d&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=1&pageSize=25&total=31&columnId=d04b9cc3da664b1995d64dca3d62be24&searchKey=',
        'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/announcements?pageNum=2&pageSize=25&total=31&columnId=d04b9cc3da664b1995d64dca3d62be24&searchKey=',
        ]
    headers = {'User-Agent': UserAgent().random}
    def start_requests(self):
        for lurl in self.start_urls:
            yield scrapy.Request(url=lurl, headers=self.headers, callback=self.parse)

    def parse(self, response, **kwargs):
        data = response.json()['data']['rows']
        for query in data:
            id = query['id']
            title = query['title']
            createTime = query['createTime']
            content_href = 'http://hgcg.customs.gov.cn/purchase/portal/portalArticle/article/' + id
            meta = {
                'title': title,
                'createTime': createTime,
            }
            yield scrapy.Request(url=content_href, callback=self.cparse, headers=self.headers, meta=meta)

    def cparse(self, response):
        item = Item()
        try:
            data = response.json()['data']
            content_html = data['content']
            result = Xpath(content_html)
            title = response.meta['title']
            date = response.meta['createTime']
            content = result.xpath("", filter="script|style")
            content_result = process_content_type(C=content)

            # filename = response.xpath("").extract() or None
            # filelink = response.xpath("").extract() or None
            # if filelink is not None and filename is not None:
            #     fileurl = ''
            #     filename = '|'.join(filename)
            #     filelink = fileurl + f'|{fileurl}'.join(filelink)

            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            # item['filename'] = filename
            # item['filelink'] = filelink
            # yield item
            print(item)

        except Exception as e:
            print(e)

if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())