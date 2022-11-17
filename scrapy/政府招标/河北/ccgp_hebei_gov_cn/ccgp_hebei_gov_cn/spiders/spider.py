import scrapy
from scrapy import cmdline
from ccgp_hebei_gov_cn.data_process import *
from ccgp_hebei_gov_cn.items import Item


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-hebei.gov.cn'
    start_urls = ['http://www.ccgp-hebei.gov.cn/province/cggg/zbgg/index.html',  # 招标公告
                  'http://www.ccgp-hebei.gov.cn/province/cggg/zhbgg/index.html',  # 中标公告
                  'http://www.ccgp-hebei.gov.cn/province/cggg/fbgg/index.html',  # 废标公告
                  'http://www.ccgp-hebei.gov.cn/province/cggg/gzgg/index.html',  # 更正公告
                  ]
    custom_settings = {
        'LOG_LEVEL': 'INFO'
    }
    listing_xpath = "//table[@id='moredingannctable']//a" + "/@href"
    def start_requests(self):
        for query in self.start_urls:
            for page in range(10):
                if page > 0:
                    url = query.replace('index', f'index_{page}')
                else:
                    url = query
                data = get_link(url, self.listing_xpath)
                for item in data:
                    lurl = '/'.join(url.split('/')[:-1])
                    lurl = lurl + item[1:]
                    yield scrapy.Request(url=lurl, callback=self.con_parse,)


    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = response.xpath("//meta[@name='ArticleTitle']/@content").get()
            date = result.dpath("//td[@class='txt7']", rule=None)
            content = result.xpath("//table[@id='2020_VERSION']", filter="script|style")

            filename = response.xpath("//a[@id='files']/text()").extract() or None
            filelink = response.xpath("//a[@id='files']/@href").extract() or None
            if filelink is not None and filename is not None:
                fileurl = ''
                filename = '|'.join(filename)
                filelink = fileurl + f'|{fileurl}'.join(filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filelink)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            print(item)

        except Exception as e:
            print(e)


# 启动
if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
