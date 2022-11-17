import scrapy
from scrapy import cmdline
from ggzyfw_beijing_gov_cn.data_process import *
from ggzyfw_beijing_gov_cn.redis_conn import *
from ggzyfw_beijing_gov_cn.items import Item

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzyfw.beijing.gov.cn'
    listing_xpath = "//a[@class='divtitlejy']/@href"
    title_xpath = "//div[@class='div-title']//text()"
    content_xpath = "//div[@class='div-article2']//text()"
    pubdate_xpath = "//div[@class='div-title2']//text()"
    custom_settings = {
        "LOG_LEVEL": 'INFO',
        'ITEM_PIPELINES': {
           'ggzyfw_beijing_gov_cn.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        }
    }
    indexpages = [129, 20, 146]
    start_urls = [
        # 采购公告
        'https://ggzyfw.beijing.gov.cn/jyxxcggg/index.html',
        # 更正事项
        'https://ggzyfw.beijing.gov.cn/jyxxgzsx/index.html',
        # 成交结果公告
        'https://ggzyfw.beijing.gov.cn/jyxxzbjggg/index.html',
    ]

    def start_requests(self):
        for i in range(3):
            condition = True
            for page in range(self.indexpages[i]+1):
                if page > 0:
                    page = str(page)
                    url = self.start_urls[0].replace('index', f'index_{page}')
                else:
                    url = self.start_urls[0]

                urls = get_link(url, self.listing_xpath)
                for link in urls:
                    link = 'https://' + self.host + link
                    # yield scrapy.Request(url=link, callback=self.cparse)

                    conn = redis_conn()
                    result = conn.find_data(value=link)
                    if result is False:
                        yield scrapy.Request(url=link, callback=self.con_parse)
                        # print(link)
                    else:
                        condition = False
                if condition is False:
                        break

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = response.xpath("//meta[@http-equiv='ArticleTitle']/@content").get()
            date = result.dpath("//div[@class='div-title2']", rule=None)
            content = result.xpath("//div[@class='newsCon']", filter="script|style")

            # filename = response.xpath("").extract() or None
            # filelink = response.xpath("").extract() or None
            # if filelink is not None and filename is not None:
            #     fileurl = ''
            #     filename = '|'.join(filename)
            #     filelink = fileurl + f'|{fileurl}'.join(filelink)
            # item['filename'] = filename
            # item['filelink'] = filelink
            content_result = process_content_type(C=content)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            # print(item)
            yield item

        except Exception as e:
            print(e)


if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
