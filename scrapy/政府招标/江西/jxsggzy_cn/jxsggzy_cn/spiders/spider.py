import scrapy, pymysql, time
from jxsggzy_cn.redis_conn import redis_conn
from jxsggzy_cn.data_process import *
from jxsggzy_cn.items import Item
from jxsggzy_cn.settings import *


class SpiderSpider(scrapy.Spider):
    '''
    采集类型: 政府招标
    目标网站: https://www.jxsggzy.cn/jyxx/trade.html（2022-11-15）
    采集时间范围: 最多采集一千页(约一到三个月内)
    :return
    '''
    name = 'spider'
    host = 'jxsggzy.cn'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888,  # 5.0
        },
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {
            f'{BOT_NAME}.ProxyMiddlewares.UserAgentDownloadMiddleware': 300,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            # f'{BOT_NAME}.ProxyMiddlewares.ProxyMiddleware': 300,
        },

        # 下载周期
        'DOWNLOAD_DELAY': 1,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,  # 想重试几次就写几

    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    start_pages = [1000]
    condition = True

    def start_requests(self):
        pn = 0
        start_time = get_datetime_now(reduce_months=3)
        end_time = get_datetime_now()
        for page in range(self.start_pages[0] + 1):
            url = ['https://www.jxsggzy.cn/XZinterface/rest/esinteligentsearch/getFullTextDataNew']  # 政府采购
            data = '{' \
                   f'"token":"","pn":{pn},"rn":10,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"",' \
                   '"sort":"{\\"webdate\\":\\"0\\",\\"id\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"",' \
                   '"condition":[{"fieldName":"categorynum","equal":"002006","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":[{"fieldName":"webdate",' \
                   f'"startTime":"{start_time} 00:00:00","endTime":"{end_time} 23:59:59"' \
                   '}],"highlights":"","statistics":null,"unionCondition":[],"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}'
            pn += 10
            if self.condition is True:
                yield scrapy.Request(url=url[0], callback=self.lparse, body=data, method='POST', headers=self.headers)
            else:
                print('已存在:')
                break

    def lparse(self, response):
        conn = redis_conn()
        result = response.json().get('result')
        if result:
            records = result.get('records')
            for info in records:
                linkurl = info.get('linkurl')
                infodate = info.get('infodate')
                title = info.get('title')
                lurl = urljoin('https://www.jxsggzy.cn/', linkurl)
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.con_parse, meta={'infodate': infodate, 'title': title})
                else:
                    print('已存在:', lurl)
                    self.condition = False
        else:
            pass

    def con_parse(self, response):
        item = {}
        title = response.meta['title']
        date = response.meta['infodate']
        content = response.text

        content_result = process_content_type(C=content)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['pagesource'] = content
        item['contenttype'] = content_result
        yield item


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
