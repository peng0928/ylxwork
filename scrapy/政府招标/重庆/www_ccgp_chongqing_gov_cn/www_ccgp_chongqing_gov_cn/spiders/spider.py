import scrapy
from www_ccgp_chongqing_gov_cn.data_process import *
from www_ccgp_chongqing_gov_cn.redis_conn import *
from www_ccgp_chongqing_gov_cn.items import Item


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/new?__platDomain__=www.ccgp-chongqing.gov.cn&endDate=2022-08-02&isResult=1&pi=2&ps=20&startDate=2021-08-02']
    host = 'www.ccgp-chongqing.gov.cn'

    endDate = get_datetime_now()
    startDate = get_datetime_now(reduce=1)
    # redis断点 采集时间范围 2021-08-02 ~ 2022-08-02

    def start_requests(self):
        for page in range(1,1043):
            condition = True
            url = f'https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/new?__platDomain__=www.ccgp-chongqing.gov.cn&endDate={self.endDate}&isResult=1&pi={page}&ps=20&startDate={self.startDate}'

            notices = get_link_json(url=url)['notices']
            for query in notices:
                url = 'https://www.ccgp-chongqing.gov.cn/gwebsite/api/v1/notices/stable/' + str(query['id'])

                conn = redis_conn()
                result = conn.find_data(value=url)
                if result is False:
                    yield scrapy.Request(url=url, callback=self.con_parse)
                else:
                    print('已存在:', url)
                condition = False
            if condition is False:
                break

    def con_parse(self, res):
        item = Item()
        notice = res.json()['notice']
        title = notice['title']
        date = notice['issueTime']
        html = notice['html']
        content = Xpath(response=html)
        content = content.xpath('', filter='style|h2|h3')
        content = process_text(content)
        date = process_date(data=date,)
        content_result = process_content_type(C=content)

        item['host'] = self.host
        item['pageurl'] = res.url
        item['docsubtitle'] = title
        item['publishdate'] = date
        item['contenttype'] = content_result
        item['doc_content'] = content
        # print(item)
        yield item


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())