# https://zfcg.czt.zj.gov.cn/
# https://zfcg.czt.zj.gov.cn/purchaseNotice/index.html

import scrapy, pymysql, time
from zfcg_czt_zj_gov_cn.redis_conn import redis_conn
from zfcg_czt_zj_gov_cn.data_process import *
from zfcg_czt_zj_gov_cn.items import Item
from zfcg_czt_zj_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'zfcg.czt.zj.gov.cn'
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

    start_pages = [22, 666, 666, 666, 666, 666]

    def start_requests(self):
        for i in range(6):
            condition = True
            for page in range(1, self.start_pages[i]+1):
                start_urls = [
                    # 资格预审公告
                    f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&pageNo={page}&sourceAnnouncementType=3009%2C4004%2C3008%2C2001&isGov=true&url=notice',
                    # 招标公告
                    f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&pageNo={page}&sourceAnnouncementType=3001%2C3020%2C2004%2C2005&isGov=true&url=notice',
                    # 非招标公告（竞争性谈判、竞争性磋商、询价公告）
                    f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&pageNo={page}&sourceAnnouncementType=3003%2C3002%2C3011&isGov=true&url=notice',
                    # 更正公告
                    f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&pageNo={page}&sourceAnnouncementType=3017%2C3018%2C3005%2C3006%2C3015&isGov=true&url=notice',
                    # 中标（成交）结果公告
                    f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&pageNo={page}&sourceAnnouncementType=3004%2C4005%2C4006%2C4009%2C8043&isGov=true&url=notice',
                    # 废标公告
                    f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&pageNo={page}&sourceAnnouncementType=3007%2C3015&isGov=true&url=notice',

                ]
                url = start_urls[i]
                query = get_link_json(url)['articles']
                for data in query:
                    id = data['id']
                    lurl = f'https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?noticeId={id}%26utm&url=noticeDetail'

                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break


    def con_parse(self, res):
        item = Item()
        try:
            res_json = res.json()
            title = res_json['noticeTitle']
            date = res_json['noticePubDate']
            result = res_json['noticeContent']
            result = Xpath(result)
            content = result.xpath("", filter='style|script')

            file = result.fxpath("//ul//a")
            filename = file[0]
            filelink = file[1]

            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filename)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = date
            item['contenttype'] = content_result
            item['doc_content'] = content
            yield item
            # print(item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
