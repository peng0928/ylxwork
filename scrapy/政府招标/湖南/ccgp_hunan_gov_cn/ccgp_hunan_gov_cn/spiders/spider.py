import scrapy, datetime
from ccgp_hunan_gov_cn.data_process import *
from ccgp_hunan_gov_cn.redis_conn import *
from ccgp_hunan_gov_cn.items import CcgpHunanGovCnItem

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ccgp-hunan.gov.cn'

    endDate = get_datetime_now()
    startDate = get_datetime_now(reduce=1)

    def start_requests(self):
        url = 'http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.ccgp-hunan.gov.cn',
            'Origin': 'http://www.ccgp-hunan.gov.cn',
            'Referer': 'http://www.ccgp-hunan.gov.cn/page/notice/more.jsp',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        for page in range(1, 701):
            condition = True
            data = f'pType=&prcmPrjName=&prcmItemCode=&prcmOrgName=&startDate={self.startDate}&endDate={self.endDate}&prcmPlanNo=&page={page}&pageSize=18'
            rows = post_link_json(url=url, data=data, headers=headers)['rows']
            for query in rows:
                NOTICE_ID = query['NOTICE_ID']
                lurl = 'http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?noticeId=' + str(NOTICE_ID)
                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, headers=headers, callback=self.con_parse)
                else:
                    print('已存在:', lurl)
                    condition = False
            if condition is False:
                break

    def con_parse(self, res):
        item = CcgpHunanGovCnItem()
        result = Xpath(res.text)
        title = result.xpath("//h2|//p[@class='danyi_title']|//h1")
        date = result.dpath("//body", rule='公告日期：|公告时间：')
        content = result.xpath("//body", filter="script|style")
        content_result = process_content_type(C=content)

        item['host'] = self.host
        item['pageurl'] = res.url
        item['docsubtitle'] = title
        item['publishdate'] = date
        item['contenttype'] = content_result
        item['doc_content'] = content
        # print(item)
        yield item


############################ 启动
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())