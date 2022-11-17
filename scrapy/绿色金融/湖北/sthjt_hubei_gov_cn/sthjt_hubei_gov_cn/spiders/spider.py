import scrapy, re, os
from sthjt_hubei_gov_cn.data_process import *
from sthjt_hubei_gov_cn.redis_conn import *
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
        'http://sthjt.hubei.gov.cn/fbjd/xxgkml/cfqz/xzcfjd/index.shtml',
        'http://sthjt.hubei.gov.cn/fbjd/xxgkml/cfqz/xzcfjd/index_1.shtml',
        'http://sthjt.hubei.gov.cn/fbjd/xxgkml/cfqz/xzcfjd/index_2.shtml',
        'http://sthjt.hubei.gov.cn/fbjd/xxgkml/cfqz/xzcfjd/index_3.shtml',
    ]
    condition = True
    dic = []
    def start_requests(self):
        for lurl in self.start_urls:
            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse, dont_filter=True)
            else:
                break

    def lparse(self, response):
        urls = response.xpath("//div[@class='article-box']/ul[@class='info-list']/li/a")
        for query in urls:
            title = query.xpath('.//text()').get()
            if '处罚决定书' in title:
                lurl = query.xpath('.//@href').get()

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    print('已存在:', lurl)
                    self.condition = False

    def cparse(self, response):
        cresult = Xpath(response.text)
        img = cresult.xpath("//div[@class='article-box']//img/@src", is_list=True)
        if img:
            pass
        else:
            content = cresult.xpath("//div[@class='article-box']|//div[@class='TRS_PreAppend']", filter='style|script', character=False)
            item = {}
            Penalty_date = cresult.dpath("//table[@class='table table-bordered']/tbody/tr[2]/td[2]") # 处罚日期
            Penalty_doc_num = cresult.xpath("//div[@class='article-box']//tbody/tr[3]/td[1]")  # 处罚文书号
            Company_name = cresult.xpath("//div[@class='article']/h2")  # 单位名称
            Company_name = re.findall('(（|\()(.*?)(）|\))', Company_name)[0][1]
            if '环境违法行为' in content:
                Offences = re.findall('(环境违法行为)(.*?)以上事实', content)[0][1].replace('：', '')  # 违法事由
            else:
                Offences = re.findall('(一、环境违法事实和证据)(.*?)二、', content)[0][1].replace('：', '')  # 违法事由

            # 处罚依据
            if '依据、种类' in content:
                Punishment_basis = re.findall('(依据、种类)(.*?)(三、)', content)[0][1]
            else:
                Punishment_basis = re.findall('(期限根据|采纳。依据|种类依据)(.*?)(的规定)', content)[0][1]
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            if '我厅决定' in content:
                Penalty_content = re.findall('(我厅决定)(.*?)(三、|根据《)', content)[0][1]  # 处罚内容
            else:
                Penalty_content = re.findall('(我厅对你单位作出如下行政处罚:|我厅决定责令你公司|以下处理和处罚：|行政处罚：|以下行政处理和处罚：|连续处罚：|以下处罚：)(.*?)(三、|根据《)', content)[0][1]  # 处罚内容
            Penalty_content = process_text(Penalty_content)
            penalty_unit = '湖北省生态环境厅'  # 处罚单位

            #处罚金额
            if '罚款' in Penalty_content:
                if '合计处罚款人民币' in Penalty_content:
                    Penalty_amount = re.findall('(合计处罚款人民币)(.*?)(（|元。)', Penalty_content)[0][1]
                else:
                    Penalty_amount = re.findall('(共计罚款|罚款|共处|，并处)(.*?)(元)', Penalty_content)[0][1]
                if '，计' in Penalty_amount:
                    Penalty_amount = re.findall('，计(.*?)元', Penalty_content)[0].replace('（', '').replace('）', '')
                if include_number(Penalty_amount):
                    if '万' not in Penalty_amount:
                        Penalty_amount = Penalty_amount.replace('元', '').replace('罚款', '')
                    if '万' in Penalty_amount:
                        Penalty_amount = float(Penalty_amount.replace('元', '').replace('罚款', '').replace('万', '').replace('人民币', '')) * 10000
                else:
                    Penalty_amount = chinese2digits(Penalty_amount.replace('罚款', '').replace('元', '').replace('人民币', ''))

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
            item['pageurl'] = response
            yield item


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute('scrapy crawl spider'.split())
