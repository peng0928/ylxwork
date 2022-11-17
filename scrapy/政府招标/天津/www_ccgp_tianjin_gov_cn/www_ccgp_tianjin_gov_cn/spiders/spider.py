# 天津市政府采购中心 http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1665&ver=2&st=1
# date： 2022-09-07
import scrapy, time, random, re
from www_ccgp_tianjin_gov_cn.data_process import *
from scrapy import cmdline
from www_ccgp_tianjin_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    timestamp = int(time.time() * 1000)
    start_urls = [
        # 采购公告-市级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1665&ver=2&st=1&stmp={timestamp}',
        # 采购公告-区级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1664&ver=2&st=1&stmp={timestamp}',
        # 更正公告-市级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1663&ver=2&st=1&stmp={timestamp}',
        # 更正公告-区级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1666&ver=2&st=1&stmp={timestamp}',
        # 采购结果公告-市级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2014&ver=2&st=1&stmp={timestamp}',
        # 采购结果公告-区级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2013&ver=2&st=1&stmp={timestamp}',
        # 合同及验收公告-市级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2015&ver=2&st=1&stmp={timestamp}',
        # 合同及验收公告-区级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2016&ver=2&st=1&stmp={timestamp}',
        # 采购意向公开-市级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2021&ver=2&st=1&stmp={timestamp}',
        # 采购意向公开-区级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2022&ver=2&st=1&stmp={timestamp}',
        # 单一来源公示-市级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2033&ver=2&st=1&stmp={timestamp}',
        # 采购意向公开-区级
        f'http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2034&ver=2&st=1&stmp={timestamp}',
    ]
    host = 'www.ccgp-tianjin.gov.cn'
    headers = {
        'Cookie': 'HttpOnly; insert_cookie=24822820; JSESSIONID=cw0caO79w_1Mtq_wJfKvtCgQm7NREPbun6uZrmrvvaOm9KM0QNQh!947598618',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    post_url = 'http://www.ccgp-tianjin.gov.cn/portal/topicView.do'
    condition = True
    def start_requests(self):
        page_list = [3172, 5481, 713, 1333, 3606, 5789, 8615, 12781, 569, 1032, 367, 276]
        for i in range(len(self.start_urls)):
            self.condition = True
            for page in range(1, int(page_list[i]) + 1):
                print('   ********当前个数：{}, 当前页数：{}********'.format(i, page))
                id = re.findall('id=(\d+)', self.start_urls[i])[0]
                data = f'method=view&page={page}&id={id}&step=1&view=Infor&st=1&ldateQGE=&ldateQLE='
                if self.condition is True:
                    yield scrapy.Request(url=self.post_url, body=data, method='POST', headers=self.headers,
                                         callback=self.lparse, meta={'data': data})
                else:
                    break

    def lparse(self, response):
        conn = redis_conn()
        get_link = response.xpath("//div[@id='reflshPage']/ul[@class='dataList']/li/a/@href").getall()
        date = response.xpath("//span[@class='time']/text()").getall()
        for query in range(len(get_link)):
            lurl = 'http://www.ccgp-tianjin.gov.cn/portal/documentView.do?method=view&id={}&ver=2'.format(
                re.findall('id=(\d+)', get_link[query])[0])
            pubdate = date[query]

            result = conn.find_data(value=1)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse, meta={'pubdate': pubdate})

            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        item = {}
        pubdate = response.meta['pubdate']
        cresult = Xpath(response.text)
        title = cresult.xpath("//meta[@name='ArticleTitle']/@content")
        content = cresult.xpath("//div[@id='pageContent']/div[@class='pageInner']",
                                filter="div[@id='crumbs']|style|script")
        file = cresult.fxpath("//div[@id='pageContent']/div[@class='pageInner']//a",
                              rule='http://www.ccgp-tianjin.gov.cn')
        filename = file[0]
        filelink = file[1]
        content_result = process_content_type(C=content, F=filename)

        item['host'] = self.host
        item['pageurl'] = response.url
        item['docsubtitle'] = title
        item['contenttype'] = content_result

        item['publishdate'] = pubdate
        item['pagesource'] = response.text
        item['filename'] = filename
        item['filelink'] = filelink
        yield item

if __name__ == '__main__':
    cmdline.execute('scrapy crawl spider'.split())