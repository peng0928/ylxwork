import scrapy, requests
from scrapy import cmdline
from www_zzcg_gov_cn.items import Item
from www_zzcg_gov_cn.data_process import *
from www_zzcg_gov_cn.redis_conn import *
from lxml import etree


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {
            'www_zzcg_gov_cn.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
    }
    HOST = 'www.zycg.gov.cn'
    FileXpath = "//button[@class='info_download']/@code"

    def start_requests(self):
        for i in range(4):
            condition = True
            for page in range(1, 21):

                start_urls = [
                    # 采购公告
                    'http://www.zzcg.gov.cn/zbgg/index.jhtml',
                    # 变更公告
                    'http://www.zzcg.gov.cn/bggg/index.jhtml',
                    # 结果公告
                    'http://www.zzcg.gov.cn/jggg/index.jhtml',
                    # 其它公告
                    'http://www.zzcg.gov.cn/qtgg/index.jhtml',
                ]
                if page > 1:
                    url = start_urls[i].replace('index', f'index_{page}')
                else:
                    url = start_urls[i]

                resp = requests.get(url=url)
                tree = etree.HTML(resp.text)
                query = tree.xpath("//div[@class='List2 Top5']/ul/li/a/@href")
                for lurl in query:
                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break


    def con_parse(self, response):
        item = Item()
        tree = Xpath(response.text)
        docusbtitle = tree.xpath("//h1[starts-with(@class,'TxtCenter')]|//h4[@class='info-title']")
        pubdate = tree.dpath("//div[starts-with(@class,'TxtCenter Gray')]")
        pageurl = response.url
        content = tree.xpath("//div[@class='Content']")

        filename = response.xpath("//div[@class='Content']/a/text()").extract() or None
        filelink = response.xpath("//div[@class='Content']/a/@href").extract() or None
        if filelink is not None and filename is not None:
            filename = '|'.join(filename)
            filelink = 'http://www.zzcg.gov.cn' + '|http://www.zzcg.gov.cn'.join(filelink)

        contenttype = process_content_type(C=content, F=filename)
        item['host'] = self.HOST
        item['pageurl'] = pageurl
        item['publishdate'] = pubdate
        item['docsubtitle'] = docusbtitle
        item['doc_content'] = content
        item['contenttype'] = contenttype
        item['filename'] = filename
        item['filelink'] = filelink
        # print(item)
        yield item


if __name__ == '__main__':
    cmdline.execute(f"scrapy crawl {SpiderSpider.name}".split())
