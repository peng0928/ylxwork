import scrapy
from urllib.parse import urljoin
from hbepb_hebei_gov_cn.data_process import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://hbepb.hebei.gov.cn/hbhjt/zwgk/fdzdgknr/xingzhengzhifa/xingzhengchufa/']

    def parse(self, response, **kwargs):
        urls = response.xpath("//a[@class='titleBT']/@href").getall()
        for url in urls:
            lurl = urljoin('http://hbepb.hebei.gov.cn', url)
            yield scrapy.Request(url=lurl, callback=self.cparse)

    def cparse(self, response):
        item = {}
        cresult = Xpath(response.text)
        content = cresult.xpath("//div[@class='p_nei']/div[@id='BodyLabel']", character=False)

        Penalty_date = re.findall('(强制执行。)(.*)', content)[0][1]  # 处罚日期
        Penalty_date = process_date(Penalty_date)  # 处罚日期

        Penalty_doc_num = '冀环罚' + re.findall('冀环罚(.*?)号', content)[0] + '号'  # 处罚文书号
        Company_name = re.findall('号(.*?)：', content)[0]  # 单位名称
        Offences = re.findall('环境违法行为：(.*?)以上事实', content)[0]  # 违法事由

        # 处罚依据
        Punishment_basis = re.findall('(依据)(.*?)的规定', content)[0][1]
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        Penalty_content = re.findall('下行政处罚：(.*?)限你单位自收到本处罚', content)[0]  # 处罚内容
        penalty_unit = '河北省生态环境厅'  # 处罚单位

        #处罚金额
        if '罚款' in Penalty_content:
            Penalty_amount = re.findall('(罚款)(.*?)(元)', Penalty_content)[0][1]
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
