import scrapy, pymysql, time, json
from www_ccgp_guangxi_gov_cn.redis_conn import redis_conn
from www_ccgp_guangxi_gov_cn.data_process import *
from www_ccgp_guangxi_gov_cn.items import Item
from www_ccgp_guangxi_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-guangxi.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 5,
        'CONCURRENT_REQUESTS': 32,
    }

    start_datas = [
        # 采购公告-公开招标公告
        '{"categoryCode":"ZcyAnnouncement3001","pageSize":"15","pageNo":1}',
        # 采购公告-竞争性谈判公告
        '{"categoryCode":"ZcyAnnouncement3002","pageSize":"15","pageNo":1}',
        # 采购公告-询价公告
        '{"categoryCode":"ZcyAnnouncement3003","pageSize":"15","pageNo":1}',
        # 采购公告-公开招标资格预审公告
        '{"categoryCode":"ZcyAnnouncement2001","pageSize":"15","pageNo":1}',
        # 采购公告-邀请招标资格预审公告
        '{"categoryCode":"ZcyAnnouncement3008","pageSize":"15","pageNo":1}',
        # 采购公告-竞争性磋商公告
        '{"categoryCode":"ZcyAnnouncement3011","pageSize":"15","pageNo":1}',
        # 采购公告-其他采购项目公告
        '{"categoryCode":"ZcyAnnouncement2002","pageSize":15,"pageNo":1}',
        # 采购公告-允许采购进口产品公示
        '{"categoryCode":"ZcyAnnouncement3013","pageSize":15,"pageNo":1}',
        # 采购公告-邀请招标公告
        '{"categoryCode":"ZcyAnnouncement3020","pageSize":15,"pageNo":1}',
        # 结果公告-中标（成交）结果公告
        '{"categoryCode":"ZcyAnnouncement3004","pageSize":15,"pageNo":1}',
        # 结果公告-中标公告
        '{"categoryCode":"ZcyAnnouncement4005","pageSize":15,"pageNo":1}',
        # 结果公告-成交公告
        '{"categoryCode":"ZcyAnnouncement4006","pageSize":15,"pageNo":1}',
        # 结果公告-邀请招标资格入围公告
        '{"categoryCode":"ZcyAnnouncement3009","pageSize":15,"pageNo":1}',
        # 结果公告-废标公告
        '{"categoryCode":"ZcyAnnouncement3007","pageSize":15,"pageNo":1}',
        # 结果公告-终止公告
        '{"categoryCode":"ZcyAnnouncement3015","pageSize":15,"pageNo":1}',
        # 结果公告-公开招标资格入围公告
        '{"categoryCode":"ZcyAnnouncement4004","pageSize":15,"pageNo":1}',
        # 结果公告-其他采购结果公告
        '{"categoryCode":"ZcyAnnouncement4007","pageSize":15,"pageNo":1}',
        # 合同公告-采购合同公告
        '{"categoryCode":"ZcyAnnouncement3010","pageSize":15,"pageNo":1}',
    ]

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Host': 'www.ccgp-guangxi.gov.cn',
        'Origin': 'http://www.ccgp-guangxi.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    def start_requests(self):
        for i in range(len(self.start_datas)):
            condition = True
            for page in range(1,661):
                proxy = req_proxies()
                url = 'http://www.ccgp-guangxi.gov.cn/front/search/category'

                data = self.start_datas[i].replace('"pageNo":1',f'"pageNo":{page}')
                res = post_link_json(url=url, proxies=proxy, headers=self.headers, data=data)
                hits = res.get('hits', None).get('hits', None)
                time.sleep(5)
                if not hits:
                    break
                else:
                    for item in hits:
                        url = 'http://www.ccgp-guangxi.gov.cn' + item['_source']['url']
                        conn = redis_conn()
                        result = conn.find_data(value=url)
                        if result is False:
                            yield scrapy.Request(url=url, headers=self.headers, callback=self.con_parse)
                        else:
                            print('已存在:', url)
                            condition = False
                    if condition is False:
                        break

    def con_parse(self, response):
        item = Item()
        try:
            input = response.xpath("//input/@value").getall()[2]
            res_json = json.loads(input)
            title = res_json['title']
            publishDate = res_json['publishDate']
            data1 = res_json['content']
            data = Xpath(data1)
            content = data.xpath('', filter='style|script')
            file = data.fxpath("//a")

            filename = file[0]
            filelink = file[1]
            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filelink)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = publishDate
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            print(data1)
            # yield item

        except Exception as e:
            print(e)



############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
