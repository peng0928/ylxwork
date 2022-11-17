# http://ccgp-bingtuan.gov.cn/
import scrapy, pymysql, time, json
from ccgp_bingtuan_gov_cn.redis_conn import redis_conn
from ccgp_bingtuan_gov_cn.data_process import *
from ccgp_bingtuan_gov_cn.items import Item
from ccgp_bingtuan_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ccgp-bingtuan.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3
        # 'CONCURRENT_REQUESTS': 32
    }

    start_datas = [
        # 采购意向
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement11","pageSize":"15","pageNo":"2"}',
        # 采购项目公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement2","pageSize":"15","pageNo":"2"}',
        # 采购公示
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement1","pageSize":"15","pageNo":"2"}',
        # 采购结果公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement4","pageSize":"15","pageNo":"2"}',
        # 采购合同公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement5","pageSize":"15","pageNo":"2"}',
        # 澄清变更公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement3","pageSize":"15","pageNo":"2"}',
        # 废标公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement10","pageSize":"15","pageNo":"2"}',
        # 电子卖场公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement8","pageSize":"15","pageNo":"2"}',
        # 非政府采购公告
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement9","pageSize":"15","pageNo":"2"}',
        # 中小企业预留份额执行情况公示
        '{"utm":"sites_group_front.2ef5001f.0.0.dd9aa28013e911ed91d361ad1d8fad3c","categoryCode":"ZcyAnnouncement14001","pageSize":"15","pageNo":"2"}',

    ]
    start_pages = [191, 660, 106, 660, 560, 660, 78, 660, 49, 27]

    def start_requests(self):
        for i in range(10):
            condition = True
            for page in range(1, self.start_pages[i] + 1):
                url = 'http://ccgp-bingtuan.gov.cn/front/search/category'
                data = self.start_datas[i].replace('"pageNo":"2"', f'"pageNo":"{page}"')
                query = post_link_json(url=url, data=data)['hits']['hits']
                for data in query:
                    lurl = 'http://ccgp-bingtuan.gov.cn' + data['_source']['url']

                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break
                    # pass

    def con_parse(self, res):
        item = Item()
        try:
            data = res.xpath("//input//@value").extract()[1]
            data = json.loads(data)
            title = data['title']
            publishDate = data['publishDate']
            content1 = data['content']
            result = Xpath(content1)
            content = result.xpath("", filter='style')
            content_result = process_content_type(C=content)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = publishDate
            item['contenttype'] = content_result
            item['doc_content'] = content1
            # yield item
            print(item)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
