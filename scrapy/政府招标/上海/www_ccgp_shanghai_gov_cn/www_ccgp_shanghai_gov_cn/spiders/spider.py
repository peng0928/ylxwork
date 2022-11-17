# http://www.ccgp-shanghai.gov.cn/
# http://www.ccgp-shanghai.gov.cn/ZcyAnnouncement/ZcyAnnouncement1/index.html?utm=sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330

import scrapy, pymysql, time, json
from www_ccgp_shanghai_gov_cn.redis_conn import redis_conn
from www_ccgp_shanghai_gov_cn.data_process import *
from www_ccgp_shanghai_gov_cn.items import Item
from www_ccgp_shanghai_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-shanghai.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 32,
    }

    start_pages = [
        77, 660, 660, 660, 660, 37
    ]

    def start_requests(self):
        headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': '_zcy_log_client_uuid=2022ef90-0eea-11ed-ad06-0fa914b7b4c1',
            'Host': 'www.ccgp-shanghai.gov.cn',
            'Origin': 'http://www.ccgp-shanghai.gov.cn',
            'Referer': 'http://www.ccgp-shanghai.gov.cn/ZcyAnnouncement/ZcyAnnouncement1/index.html?utm=sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',

        }
        for i in range(6):
            condition =True
            for page in range(1, self.start_pages[i] + 1):
                data = [
                    # 采购公告-单一来源公示
                    '{"utm":"sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330","categoryCode":"ZcyAnnouncement1","pageSize":"15","pageNo":"%d"}' % page,
                    # 采购公告-采购公告
                    '{"utm":"sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330","categoryCode":"ZcyAnnouncement2","pageSize":"15","pageNo":"%d"}' % page,
                    # 采购公告-更正公告
                    '{"utm":"sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330","categoryCode":"ZcyAnnouncement3","pageSize":"15","pageNo":"%d"}' % page,
                    # 采购公告-采购结果公告
                    '{"utm":"sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330","categoryCode":"ZcyAnnouncement4","pageSize":"15","pageNo":"%d"}' % page,
                    # 采购公告-采购合同公告
                    '{"utm":"sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330","categoryCode":"ZcyAnnouncement5","pageSize":"15","pageNo":"%d"}' % page,
                    # 采购公告-终止公告
                    '{"utm":"sites_group_front.2ef5001f.0.0.5dd53790147f11ed8d08ed77b0126330","categoryCode":"ZcyAnnouncement6","pageSize":"15","pageNo":"%d"}' % page,

                ]
                body = data[i]
                url = 'http://www.ccgp-shanghai.gov.cn/front/search/category'
                hits = post_link_json(url=url, data=body)['hits']['hits']
                for data in hits:
                    _source = data['_source']
                    publishDate = process_timestamp(_source['publishDate'])
                    lurl = 'http://www.ccgp-shanghai.gov.cn' + _source['url']

                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse, meta={'publishDate': publishDate})
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break

    def con_parse(self, res):
        item = Item()
        try:
            publishDate = res.meta['publishDate']
            data = res.xpath("//input/@value").extract()[2]
            data = json.loads(data)
            title = data['title']
            content = data['content']
            res_text = Xpath(content)
            text = res_text.xpath("", filter='style|script')
            file = res_text.fxpath("//a")
            filename = file[0]
            filelink = file[1]
            content_result = process_content_type(C=text, F=filename)

            item['filename'] = filename
            item['filelink'] = filelink
            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = publishDate
            item['contenttype'] = content_result
            item['doc_content'] = text
            yield item
            # print(item)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
