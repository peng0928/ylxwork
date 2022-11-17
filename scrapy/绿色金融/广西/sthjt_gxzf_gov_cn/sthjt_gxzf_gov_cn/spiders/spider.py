import scrapy, re
from urllib.parse import urljoin
from data_process import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://sthjt.gxzf.gov.cn/zfxxgk/zfxxgkgl/fdzdgknr/xzsysf/zfgs/']

    def parse(self, response, **kwargs):
        urls = response.xpath("//div[@id='morelist']/ul[@class='more-list']/li/a/@href").getall()
        for url in urls:
            lurl = 'http://sthjt.gxzf.gov.cn/zfxxgk/zfxxgkgl/fdzdgknr/xzsysf/zfgs' + url[1:]
            yield scrapy.Request(url=lurl, callback=self.cparse, dont_filter=True)

    def cparse(self, response):
        item = {}
        cresult = Xpath(response.text)
        content = cresult.xpath("//div[@class='article']/div[@class='article-con']", character=False)
        case = re.findall('案例(\d)：|案例(\w)：|。案例(\d)|：案例(\d)', content)
        len_case = len(case)
        for case_id in range(len_case):
            if case_id == len_case-1:
                id = ''.join(case[case_id])
                text = re.findall(f'案例{id}(.*)', content)
            else:
                id = ''.join(case[case_id])
                id2 = ''.join(case[case_id+1])
                text = re.findall(f'案例{id}(.*?)案例{id2}', content)

            Penalty_date = re.findall('\d{4}年\d{1,2}月\d{1,2}日', text[0])[-1]  # 处罚日期
            Penalty_doc_num = cresult.xpath("//tr[1]//td")   # 处罚文书号
            Company_name = re.findall('\d{4}年\d{1,2}月\d{1,2}日', text[0])[-1]  # 单位名称
            Offences = cresult.xpath("//tr[10]//td")   # 违法事由
        #
        # # 处罚依据
        # Punishment_basis = cresult.xpath("//tr[11]/td")
        # Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        # Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        # Punishment_basis = ','.join(Punishment_basis)
        #
        # Penalty_content = cresult.xpath("//tr[13]//td")  # 处罚内容
        # penalty_unit = '江苏省生态环境厅'  # 处罚单位
        #
        # #处罚金额
        #
        # Penalty_amount = cresult.xpath("//tr[14]//td[1]")
        # if Penalty_amount is None:
        #     Penalty_amount = ''
        # else:
        #     Penalty_amount = float(Penalty_amount)*10000
        #
        #
        # item['Penalty_date'] = Penalty_date
        # item['Penalty_doc_num'] = Penalty_doc_num
        # item['penalty_unit'] = penalty_unit
        # item['Company_name'] = Company_name
        # item['Offences'] = Offences
        # item['Punishment_basis'] = Punishment_basis
        # item['Penalty_content'] = Penalty_content
        # item['Penalty_amount'] = Penalty_amount
        # item['pageurl'] = response.url
        # yield item
        # print(item)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
