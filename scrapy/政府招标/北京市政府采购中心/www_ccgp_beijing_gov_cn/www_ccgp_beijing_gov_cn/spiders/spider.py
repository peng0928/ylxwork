import scrapy, requests
from scrapy import cmdline
from www_ccgp_beijing_gov_cn.items import Item
from www_ccgp_beijing_gov_cn.data_process import *
from www_ccgp_beijing_gov_cn.redis_conn import *
from lxml import etree

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-beijing.gov.cn'
    pageindex = [143]
    start_urls = [
        # 招标公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjzbgg/index.html',
        # 中标公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjzbjggg/index.html',
        # 合同公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjhtgg/index.html',
        # 更正公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjgzgg/index.html',
        # 废标公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjfbgg/index.html',
        # 单一公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjdygg/index.html',
        # 其他公告
        'http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjqtgg/index.html',
    ]

    def start_requests(self):
        for i in range(7):
            condition = True
            for page in range(144):
                if page > 0:
                    url = self.start_urls[i].replace('index', f'index_{page}')
                else:
                    url = self.start_urls[i]
                res = requests.get(url)
                tree = etree.HTML(res.text)
                query = tree.xpath("//div[@class='inner-l-i']/ul/li/a/@href")
                for data in query:
                    addurl = '/'.join(url.split('/')[:-1])
                    lurl = addurl + data[1:]
                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse, meta={'addurl': addurl})
                    else:
                        condition = False
                if condition is False:
                    break

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//title")
            date = result.dpath("//div[@class='xl-box-t']", rule=None)
            content = result.xpath("//div[@class='mainTextBox']/div[@id='mainText']", filter="script|style")

            filename = response.xpath("//div[@class='mainTextBox']/div[@id='mainText']//a//text()").extract() or None
            filelink = response.xpath("//div[@class='mainTextBox']/div[@id='mainText']//a/@href").extract() or None
            if filelink is not None and filename is not None:
                fileurl = response.meta['addurl']
                filename = '|'.join(filename)
                filelink = fileurl + f'|{fileurl}'.join(filelink).replace('./', '/')
            content_result = process_content_type(C=content, F=filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result

            yield item
            # print(item)

        except Exception as e:
            print(e)

if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
