import scrapy, pymysql, time
from ccgp_shandong_gov_cn.redis_conn import redis_conn
from ccgp_shandong_gov_cn.data_process import *
from ccgp_shandong_gov_cn.items import Item
from ccgp_shandong_gov_cn.settings import BOT_NAME
from ccgp_shandong_gov_cn.useragent import get_ua


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-shandong.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        # 'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 32,
    }
    redis_name = '政府招标:' + host
    condition = True

    def start_requests(self):
        start_urls = 'http://www.ccgp-shandong.gov.cn/sdgp2017/site/listnew.jsp'
        datas = [
            '&colcode=2500&curpage=1',  # 省意向公开
            '&colcode=2501&curpage=1',  # 省需求公开
            '&colcode=2502&curpage=1',  # 省合同公开
            '&colcode=2503&curpage=1',  # 省验收公开
            '&colcode=2504&curpage=1',  # 市县需求(意向)公开
            '&colcode=2505&curpage=1',  # 市县合同公开
            '&colcode=2506&curpage=1',  # 市县验收公开
        ]
        start_pages = [531, 1490, 10451, 1662, 8167, 30085, 8834]
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for i in range(7):
            self.condition = True
            for page in range(start_pages[i]):
                if self.condition is True:
                    data = datas[i].replace('curpage=1', f'curpage={str(page)}')
                    yield scrapy.Request(url=start_urls, body=data, headers=headers, method='POST', callback=self.lparse)
                if self.condition is False:
                    break

    def lparse(self, response):
        lresult = response.xpath("//span[@class='title']/span/a/@href").getall()
        for item in lresult:
            lurl = 'http://www.ccgp-shandong.gov.cn' + item
            conn = redis_conn()
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.con_parse, dont_filter=True)
            else:
                print('已存在:', lurl)
                self.condition = False

    def con_parse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = result.xpath("//h1[@class='title']")
            date = result.dpath("//div[@class='info']")
            content = result.xpath("//div[@id='textarea']")
            file = result.fxpath("//div[@id='file_list']/a")
            filename = file[0]
            filelink = file[1]
            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filelink)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = date
            item['contenttype'] = content_result
            item['doc_content'] = content
            # yield item
            print(item)

        except Exception as e:
            print(e)


############# 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
