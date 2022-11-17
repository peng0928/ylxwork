import scrapy, json
from ccgp_shanxi_gov_cn.items import Item
from ccgp_shanxi_gov_cn.pymysql_connection import pymysql_connection
from ccgp_shanxi_gov_cn.data_process import *
from ccgp_shanxi_gov_cn.redis_conn import *
from lxml import etree

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://www.ccgp-shanxi.gov.cn/front/search/category']

    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [403, 404, 400, 500],
        'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'INFO',
    }
    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Content-Length': '64',
        'Content-Type': 'application/json',
        'Host': 'www.ccgp-shanxi.gov.cn',
        'Origin': 'http://www.ccgp-shanxi.gov.cn',
        'Referer': 'http://www.ccgp-shanxi.gov.cn/ZcyAnnouncement/ZcyAnnouncement2/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',

    }
    host = 'ccgp-shanxi.gov.cn'

        ###################断点##############
    def start_requests(self):
        for ZcyAnnouncement in range(1,5):
            ZcyAnnouncement = str(ZcyAnnouncement)
            condition = True
            for page in range(1,661):
                data = {"categoryCode": f"ZcyAnnouncement{ZcyAnnouncement}","pageSize": "15","pageNo": f"{page}"}

                resp = post_link(self.start_urls[0], headers=self.headers, data=json.dumps(data))
                hits = resp['hits']['hits']
                for query in hits:
                    _source = query['_source']
                    title = _source['title']
                    url = 'http://www.ccgp-shanxi.gov.cn/' + _source['url']
                    conn = redis_conn()
                    result = conn.find_data(value=url)
                    if result is False:
                        yield scrapy.Request(url=url, callback=self.con_parse)
                    else:
                        condition = False
                if condition is False:
                    break
                    # pass

    def con_parse(self, response):
        item = Item()
        try:
            input = response.xpath("//input/@value").extract()[2]
            json_res = json.loads(input)
            content_html = json_res['content']
            title = json_res['title']
            title = process_text(title)

            createTime = str(json_res['createTime'])
            createTime = process_timestamp(createTime)

            content = Xpath(content_html)
            content = content.xpath('', filter='style')

            res = etree.HTML(content_html)
            filename = res.xpath("//a/text()") or None
            filelink = res.xpath("//a/@href") or None
            if filelink is not None and filename is not None:
                fileurl = ''
                filename = '|'.join(filename)
                filelink = fileurl + f'|{fileurl}'.join(filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filename)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = createTime
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            # print(item)
            yield item

        except Exception as e:
            print(e)





# 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
