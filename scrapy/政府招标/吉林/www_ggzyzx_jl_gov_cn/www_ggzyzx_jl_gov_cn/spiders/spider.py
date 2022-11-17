import scrapy, pymysql, time
from www_ggzyzx_jl_gov_cn.redis_conn import redis_conn
from www_ggzyzx_jl_gov_cn.data_process import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ggzyzx.jl.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            'www_ggzyzx_jl_gov_cn.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
    }
    start_urls = [
        # 政采集中-招标公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcjz/zbgg/index.html',
        # 政采集中-征求意见公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcjz/zqyjgg/index.html',
        # 政采集中-变更(延期)公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcjz/bggg/index.html',
        # 政采集中-中标(成交)结果
        'http://www.ggzyzx.jl.gov.cn/jygg/zcjz/zbjggg/index.html',
        # 政采集中-合同公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcjz/htgg/index.html',
        # 政采集中-废标(终止)公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcjz/fbgg/index.html',

        # 政采非集中-招标公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcfjz/cgzxzbgg/index.html',
        # 政采非集中-变更(延期)公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcfjz/cgzxzbgg/index.html',
        # 政采非集中-中标(成交)结果
        'http://www.ggzyzx.jl.gov.cn/jygg/zcfjz/cgzxzbgg/index.html',
        # 政采非集中-合同公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcfjz/cgzxzbgg/index.html',
        # 政采非集中-废标(终止)公告
        'http://www.ggzyzx.jl.gov.cn/jygg/zcfjz/cgzxzbgg/index.html',

    ]
    start_pages = [
        50, 17, 50, 50, 50, 26, 50, 50, 50, 50, 38
    ]
    condition = True
    def start_requests(self):
        for i in range(len(self.start_urls)):
            for page in range(self.start_pages[i] + 1):
                if page > 0:
                    url = self.start_urls[i].replace('index', f'index_{page}')
                else:
                    url = self.start_urls[i]

                if self.condition is True:
                    yield scrapy.Request(url=url, callback=self.lparse)
                    time.sleep(5)
                else:
                    break

    def lparse(self, res):
        conn = redis_conn()
        data = res.xpath("//div[@class='content_r_main']//li/a/@href").getall()
        for query in data:
            lurl = '/'.join(res.url.split('/')[:-1]) + query[1:]
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse)
                time.sleep(5)
            else:
                print('已存在:', lurl)
                # self.condition = False

    def cparse(self, res):
        item = {}

        result = Xpath(res.text)
        title = result.xpath("//div[@class='content_title_m']")
        date = result.dpath("//div[@class='content_time']", rule=None)
        content = result.xpath("//div[@class='content']/div[@class='neirong']",
                               filter="script|div[@class='content_title_m']|div[@class='time_pring']")
        file = result.fxpath("//div[@class='neirong']/div[@class='mains m_t_60']/a")
        filename = file[0]
        filelink = file[1]
        content_result = process_content_type(C=content, F=file)

        item['filename'] = filename
        item['filelink'] = filelink
        item['host'] = self.host
        item['pageurl'] = res.url
        item['docsubtitle'] = title
        item['publishdate'] = date
        item['contenttype'] = content_result
        item['doc_content'] = content
        # yield item
        print(item)