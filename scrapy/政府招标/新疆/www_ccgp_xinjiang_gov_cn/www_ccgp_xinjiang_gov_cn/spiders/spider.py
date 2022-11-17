# http://www.ccgp-xinjiang.gov.cn/
import scrapy, pymysql, time
from www_ccgp_xinjiang_gov_cn.redis_conn import redis_conn
from www_ccgp_xinjiang_gov_cn.data_process import *
from www_ccgp_xinjiang_gov_cn.items import Item
from www_ccgp_xinjiang_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.ccgp-xinjiang.gov.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            # f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        'HTTPERROR_ALLOWED_CODES': [403, 404, 400, 500],
        'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        # 'DOWNLOAD_DELAY': 0.6,
        # 'CONCURRENT_REQUESTS': 32,
    }

    start_pages = []
    
    def start_requests(self):
        headers = {
            "Content-Type": "application/json;charset=UTF-8&application/json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cookie": "acw_tc=ac11000116674637953523775e0107647eb7c0c1709eec6a74d815accc6f7a; _zcy_log_client_uuid=c74d5a00-5b50-11ed-b119-f58526cb4a6d",
            "Host": "www.ccgp-xinjiang.gov.cn",
            "Origin": "http://www.ccgp-xinjiang.gov.cn",
            "Referer": "http://www.ccgp-xinjiang.gov.cn/ZcyAnnouncement/ZcyAnnouncement1/index.html?utm=sites_group_front.4ac888e7.0.0.0bd217b05b5111ed965043fff5d68150",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        for i in range(18):
            for page in range(1, 661):
                url = 'http://www.ccgp-xinjiang.gov.cn/front/search/category'
                data = [
                    # 采购意向公开
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement10016"}'%page,
                    # 公开招标公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3001"}'%page,
                    # 竞争性谈判公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3002"}'%page,
                    # 询价公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3003"}'%page,
                    # 邀请招标资格预审公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3008"}'%page,
                    # 竞争性磋商公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3011"}'%page,
                    # 公开招标资格预审公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement2001"}'%page,
                    # 采购公示
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3020"}'%page,
                    # 中标(成交)结果公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement1"}'%page,
                    # 邀请招标资格入围公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3004"}'%page,
                    # 终止公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3009"}'%page,
                    # 采购结果变更公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3015"}'%page,
                    # 公开招标资格入围公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3017"}'%page,
                    # 中标公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement4004"}'%page,
                    # 采购合同公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3010"}'%page,
                    # 更正公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3005"}'%page,
                    # 澄清（修改）公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3006"}'%page,
                    # 中止（暂停）公告
                    '{"pageNo":"%d","pageSize":"15","categoryCode":"ZcyAnnouncement3018"}'%page,
                ]
                yield scrapy.Request(url=url, headers=headers, method='POST', body=data[i], callback=self.dparse)

    # 链接
    def dparse(self, res):
        print(res.text)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
