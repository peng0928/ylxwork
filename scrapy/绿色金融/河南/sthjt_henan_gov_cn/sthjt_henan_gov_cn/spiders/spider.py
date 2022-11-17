import scrapy, re
from sthjt_henan_gov_cn.data_process import *
from sthjt_henan_gov_cn.redis_conn import *
from fake_useragent import UserAgent


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [406, 301],
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'user-agent': UserAgent().random}
    }
    start_urls = [
        'https://sthjt.henan.gov.cn/xxgk/hbywxxgk/jdzf/index.html',
        'https://sthjt.henan.gov.cn/xxgk/hbywxxgk/jdzf/index_1.html',
    ]
    condition = True

    def start_requests(self):
        for lurl in self.start_urls:
            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse, dont_filter=True)
            else:
                break

    def lparse(self, response):
        urls = response.xpath("//div[@class='pdlist']/ul/li/a")
        for query in urls:
            title = query.xpath('.//text()').get()
            if '行政处罚决定书' in title:
                lurl = query.xpath('.//@href').get()

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    print('已存在:', lurl)
                    self.condition = False

    def cparse(self, response):

        item = {}
        cresult = Xpath(response.text)
        content = cresult.xpath("//div[@class='zwcontent']/div[@id='BodyLabel']", character=False)

        Penalty_date = re.findall('(强制执行。)(.*)', content)[0][1]  # 处罚日期
        Penalty_date = process_date(Penalty_date)  # 处罚日期

        Penalty_doc_num = '豫环' + re.findall('豫环(.*?)号', content)[0] + '号'  # 处罚文书号
        Company_name = re.findall('号(.*?)(：|统一社会信用代码)', content)[0][0]  # 单位名称
        Offences = re.findall('一、环境违法事实和证据(.*?)以上事实', content)[0]  # 违法事由

        # 处罚依据
        Punishment_basis = re.findall('(依据)(.*?)的规定', content)[0][1]
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        Penalty_content = re.findall('(作出以下处罚决定：|作出以下处理决定：)(.*?)三、行政处罚', content)[0][1]  # 处罚内容
        penalty_unit = '河南省生态环境厅'  # 处罚单位

        # 处罚金额
        if '罚款' in Penalty_content:
            Penalty_amount = re.findall('(罚款)(.*?)(元)', Penalty_content)[0][1]
            Penalty_amount = numtohans(Penalty_amount.replace('人民币', ''))
            Penalty_amount = chinese2digits(Penalty_amount)

        else:
            Penalty_amount = None

        item['Penalty_date'] = Penalty_date
        item['Penalty_doc_num'] = Penalty_doc_num
        item['penalty_unit'] = penalty_unit
        item['Company_name'] = Company_name
        item['Offences'] = Offences
        item['Punishment_basis'] = Punishment_basis
        item['Penalty_content'] = Penalty_content
        item['Penalty_amount'] = Penalty_amount
        item['pageurl'] = response.url
        yield item


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
