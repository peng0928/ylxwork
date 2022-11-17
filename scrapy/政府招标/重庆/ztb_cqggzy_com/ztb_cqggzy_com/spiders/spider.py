import scrapy, json, requests
from ztb_cqggzy_com.data_process import *
from ztb_cqggzy_com.redis_conn import *
from ..useragent import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    headers = {'User-Agent': get_ua(),
               'Content-Type': 'application/json'}
    # 爬取近3个月
    host = 'ztb.cqggzy.com'
    condition = True
    def start_requests(self):
        for page2 in range(1, 421):
            headers = {'User-Agent': get_ua(),
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            url = 'https://ztb.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoListWithSecondCateNew'
            data = f'pageIndex={page2}&pageSize=20&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005&title=&infoC=&startdate=2020-06-10+00%3A00%3A00&enddate={get_datetime_now()}+23%3A59%3A59'
            if self.condition is True:
                yield scrapy.Request(url=url, method='POST', body=data, headers=headers, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        conn = redis_conn()
        headers = {'User-Agent': get_ua()}
        custom = response.json().get('custom', None)
        result = json.loads(custom)
        for query in result:
            categorynum = query.get('categorynum', None)
            infoid = query.get('infoid', None)
            pubinwebdate = query.get('infodate', None)
            pubinwebdate = timechange(pubinwebdate)
            lurl = f'https://ztb.cqggzy.com/xxhz/{categorynum[:-3]}/{categorynum}/{pubinwebdate}/{infoid}.html'

            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, headers=headers, callback=self.cparse)
            else:
                print('已存在:',lurl)
                self.condition = False

    def cparse(self, response):
        item = {}
        result = Xpath(response.text)
        title = result.xpath("//h3[@class='article-title']|//div[@class='title-text']")
        date = result.dpath("//div[@class='info-source']", rule=None)
        content = result.xpath("//div[@id='mainContent']", filter="script|style")

        content_result = process_content_type(C=content)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = date
        item['docsubtitle'] = title
        item['doc_content'] = response.text
        item['contenttype'] = content_result
        # yield item
        print(item)



