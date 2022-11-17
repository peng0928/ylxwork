import scrapy, json
from ccgp_hubei_gov_cn.redis_conn import redis_conn
from ccgp_hubei_gov_cn.data_process import *
from ccgp_hubei_gov_cn.items import Item


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ccgp-hubei.gov.cn'
    condition = True
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=723E770089EAC87DFC35EE42A2F441F8; JSESSIONID=49C32F11CA1D25FFA4340907A35553F0',
        'Host': 'www.ccgp-hubei.gov.cn:9040',
        'Origin': 'http://www.ccgp-hubei.gov.cn:9040',
        'Referer': 'http://www.ccgp-hubei.gov.cn:9040/quSer/search',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }

    def start_requests(self):
        for page in range(1, 2310):
            start_time = get_datetime_now(reduce_months=6, rule='%Y/%m/%d')
            end_time = get_datetime_now(rule='%Y/%m/%d')
            data = 'queryInfo.type=xmgg&queryInfo.key=' \
                   '&queryInfo.jhhh=' \
                   '&queryInfo.fbr=' \
                   '&queryInfo.gglx=' \
                   '&queryInfo.cglx=' \
                   '&queryInfo.cgfs=' \
                   '&queryInfo.city=%E6%B9%96%E5%8C%97%E7%9C%81' \
                   '&queryInfo.qybm=42%3F%3F%3F%3F' \
                   '&queryInfo.district=%E5%85%A8%E7%9C%81' \
                   '&queryInfo.cgr=' \
                   f'&queryInfo.begin={start_time}' \
                   f'&queryInfo.end={end_time}' \
                   f'&queryInfo.pageNo={page}' \
                   '&queryInfo.pageSize=15'

            url = 'http://www.ccgp-hubei.gov.cn:9040/quSer/search'
            if self.condition is True:
                yield scrapy.Request(url=url, headers=self.headers, body=data, method='POST', callback=self.lparse)
            else:
                print('已存在：退出')
                break

    def lparse(self, response):
        get_ltem = response.xpath("//div[@class='title ellipsis']/a/@href").getall()
        print(get_ltem)
        conn = redis_conn()
        for link in get_ltem:
            result = conn.find_data(value=link)
            if result is False:
                yield scrapy.Request(url=link, callback=self.con_parse, dont_filter=True)
            else:
                print('已存在:', link)
                #self.condition = False
            if self.condition is False:
                break

    def con_parse(self, response):
        item = Item()
        result = Xpath(response.text)
        title = result.xpath("//div[@class='art_con']//h2")
        date = result.dpath("//div[@class='art_con']/div[1]/div", rule=None)
        content = result.xpath("//div[@class='art_con']", filter="script|style")
        content_result = process_content_type(C=content)

        item['host'] = self.host
        item['pageurl'] = response.url
        item['docsubtitle'] = title
        item['publishdate'] = date
        item['contenttype'] = content_result
        item['doc_content'] = content
        print(item)
        # yield item


############################ 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
