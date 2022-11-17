import scrapy
from hnzbcg_cn.redis_conn import redis_conn
from hnzbcg_cn.data_process import *
from hnzbcg_cn.items import Item


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://www.hnzbcg.cn/zhaobiao/list1.html',  # 招标公告
                  'http://www.hnzbcg.cn/zhaobiao/list7.html',  # 中标候选人
                  'http://www.hnzbcg.cn/zhaobiao/list8.html',  # 结果公示
                  'http://www.hnzbcg.cn/zhaobiao/list6.html'  # 变更公告
                  ]
    start_index = [1262, 4015, 14, 4]
    host = 'www.hnzbcg.cn'

    listing_xpath = "//div[@class='left fontover']/a/@href"
    def start_requests(self):
        for i in range(4):
            condition = True
            for page in range(1, self.start_index[i]):
                if page < 2:
                    url = self.start_urls[i]
                else:
                    url = self.start_urls[i].replace('.html', f'_{str(page)}.html')
                res = get_link(url, self.listing_xpath)
                for item in res:
                    item = 'http://www.hnzbcg.cn' + item
                    conn = redis_conn()
                    result = conn.find_data(value=item)
                    if result is False:
                        yield scrapy.Request(url=item, callback=self.con_parse)
                    else:
                        print('已存在：',item)
                        condition = False
                if condition is False:
                    break
                    # pass
    def con_parse(self, response):
        item = Item()
        result = Xpath(response.text)
        title = result.xpath("//div[@class='listTitle1']/h1")
        date = result.dpath("//div[@class='views']", rule='发布日期：')
        content = result.xpath("//div[@class='detail']")
        content_result = process_content_type(C=content)

        item['host'] = self.host
        item['pageurl'] = response.url
        item['docsubtitle'] = title
        item['publishdate'] = date
        item['contenttype'] = content_result
        item['doc_content'] = content
        # print(item)
        yield item



# 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
