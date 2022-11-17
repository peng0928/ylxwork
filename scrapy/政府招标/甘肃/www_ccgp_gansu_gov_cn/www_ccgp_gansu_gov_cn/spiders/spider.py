# 网站：http://www.ccgp-gansu.gov.cn/

import scrapy, pymysql, time
from www_ccgp_gansu_gov_cn.redis_conn import redis_conn
from www_ccgp_gansu_gov_cn.data_process import *
from www_ccgp_gansu_gov_cn.items import Item
from www_ccgp_gansu_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = ''
    redis_name = '政府招标:' + host
    custom_settings = {
    'ITEM_PIPELINES': {
        # f'{BOT_NAME}.pipelines.Pipeline': 300,
        # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
    },
    'LOG_LEVEL': 'INFO',

    # 允许状态码
    'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
    'COOKIES_ENABLED': False,
    # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
    # 'CONCURRENT_REQUESTS_PER_IP': 16
    # 'DOWNLOAD_DELAY': 0.6
    # 'CONCURRENT_REQUESTS': 32
}


    ############读取redis数据库爬取############
    # def start_requests(self):
    #     conn = redis_conn()
    #     result = conn.get_data(field=redis_name)  # '政府招标:
    #     for query in result:
    #         url = str(query, encoding='utf-8')
    #         yield scrapy.Request(url=url, callback=self.cparse)
    #
    #
    # def cparse(self, res):
    #     item = Item()
    #     try:
    #         result = Xpath(res.text)
    #         title = result.xpath("")
    #         date = result.dpath("", rule=None)
    #         content = result.xpath("", filter=None)
    #         content_result = process_content_type(C=content)
    #
    #         item['host'] = self.host
    #         item['pageurl'] = res.url
    #         item['docsubtitle'] = title
    #         item['publishdate'] = date
    #         item['contenttype'] = content_result
    #         item['doc_content'] = content
    #         yield item
    #     # print(item)
    #
    #     except Exception as e:
    #         print(e)


    start_pages  = []
    headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Connection': 'keep-alive',
'Cookie': '4hP44ZykCTt5S=5vTtEmFcMA4K8ZRSX1g.Iz7B7xnn.9dCLcjUNhe4t5UPwjBezOo4v1Rosrc3yLZv2J4fcu71RrpH6u.CSA3UDfG; JSESSIONID=540E51B3EAF8C50FC00A934686CE03E2.tomcat3; 4hP44ZykCTt5T=B5O.vakFIIdJha4OFdpp1gMIHC0MBRHaV5_zQHUIbm8lqxTA3UNBr9s3EQixHsWXepb_jy8GnDnXhtY9.l0qKp.4efE7SVfzfPKqcvmVyGUAc6xKEbJ_O82B70EZTOp_vHRUssptSt5jphRIn98wOiONXPXheJH4wSzfIhdUVyhCVyxznF6CtZdGQ7ucZr127CwaQfRRnMzf2Sd6Iz5E6jcdT.8_EVqXsyCbNfh_ZAVmzSPCDBRuSOF9JUebpwh.fUuOw3Yi6joYPaj07vYjhV9VSn4knk0SAy41J_JXSiafmNyWpbnI8UGRLftnz13rPNstukf_iSMQTIP45ddB3wjmsq6mmMYoje2mUPlioP3DuYU6bm9N4aR0dZtDtvzIueEaX7vZnyMvNVvVFjyIKG',
'Host': 'www.ccgp-gansu.gov.cn',
'Referer': 'http://www.ccgp-gansu.gov.cn/web/doSearchmxarticlelssj.action?limit=20&start=60',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    def start_requests(self):
        for page in range(1):
            url = f'http://www.ccgp-gansu.gov.cn/web/doSearchmxarticlelssj.action?limit=20&start=40'
            yield scrapy.Request(url=url,headers=self.headers, callback=self.dparse)

    def dparse(self, res):
        try:
            r = redis_conn()
            query = res.xpath("//div[@class='mBd']//li/a/@href").extract()
            for item in query:
                url = 'http://www.ccgp-shandong.gov.cn' + item
                print(url)
                # r.set_add(field=redis_name, value=url)

        except Exception as e:
            print(e)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
