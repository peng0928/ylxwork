import scrapy, re
from urllib.parse import urljoin
from data_process import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://218.94.78.61:9081/sgs/business/sgs/wzsgs/sgscontroller/sgsXzcfGsList']

    def parse(self, response, **kwargs):
        urls = response.xpath("//ul[@class='main-list']/li/a/@onclick").getall()
        for url in urls:
            re_url = re.findall("'(.*?)'", url)[0]
            lurl = 'http://218.94.78.61:9081/sgs/business/sgs/wzsgs/sgscontroller/XzcfGsView?XH=' + re_url
            # print(lurl)
            yield scrapy.Request(url=lurl, callback=self.cparse)

    def cparse(self, response):
        item = {}
        cresult = Xpath(response.text)

        Penalty_date = cresult.dpath("//tr[16]//td")  # 处罚日期

        Penalty_doc_num = cresult.xpath("//tr[1]//td")   # 处罚文书号
        Company_name = cresult.xpath("//tr[2]//td")  # 单位名称
        Offences = cresult.xpath("//tr[10]//td")   # 违法事由

        # 处罚依据
        Punishment_basis = cresult.xpath("//tr[11]/td")
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        Penalty_content = cresult.xpath("//tr[13]//td")  # 处罚内容
        penalty_unit = '江苏省生态环境厅'  # 处罚单位

        #处罚金额

        Penalty_amount = cresult.xpath("//tr[14]//td[1]")
        if Penalty_amount is None:
            Penalty_amount = ''
        else:
            Penalty_amount = float(Penalty_amount)*10000


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
        # print(item)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
