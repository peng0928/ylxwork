import scrapy
from ..data_process import *
from ..redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'lnspider'
    start_urls = ['http://sthj.ln.gov.cn/hjgl/zfgl/xzcf/index.html']
    condition = True

    def start_requests(self):
        for page in range(4):
            if page > 0:
                lurl = self.start_urls[0].replace('index', f'index_{page}')
            else:
                lurl = self.start_urls[0]

            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse)
            else:
                break
                # pass

    def lparse(self, response):
        lresult = response.xpath("//div[@class='zy_list2']/ul/li/a")
        for query in lresult:
            title = query.xpath(".//text()").get()
            if '决定' in title:
                lurl = 'http://sthj.ln.gov.cn/hjgl/zfgl/xzcf' + query.xpath('.//@href').get()[1:]
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
        content = cresult.xpath("//div[@class='zy_content']/div[@class='zy_text']", character=False, filter='style|script')
        if '行政处罚决定书' in content:
            content = content.split('行政处罚决定书')
        if '责令改正违法行为决定书' in content:
            content = content.split('责令改正违法行为决定书')
        content.remove('')
        if '\n' in content:
            content.remove('\n')
        count = content.count('')
        if count >= 1:
            content.remove('')
        for text in content:

            if '行政命令下达日期' in text:
                Penalty_date = re.findall('行政命令下达日期：(.*?)命令作出机关', text)  # 处罚日期
                Penalty_date = ''.join(Penalty_date).replace('年', '-').replace('月', '-').replace('日', '')
            else:
                Penalty_date = cresult.dpath("//div[@class='info']", rule="时间：")

            Penalty_doc_num = re.findall('（(.*?)(）被处罚|）当事人名称)', text)[0][0]  # 处罚文书号

            Company_name = re.findall('(当事人名称：|被处罚者名称：)(.*?)违法事实：', text)[0][1]  # 单位名称

            Offences = re.findall('(违法事实：)(.*?)(处罚依据：|行政命令作出的依据：)', text)[0][1]  # 违法事由

            # 处罚依据
            Punishment_basis = re.findall('(行政命令作出的依据：|处罚依据：)(.*?)(改正违法行为的期限：|处罚内容：)', text)
            Punishment_basis = [i[1] for i in Punishment_basis]
            Punishment_basis = ''.join(Punishment_basis)
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            Penalty_content = re.findall('(改正违法行为的期限：|处罚内容：)(.*?)(改正违法行为的具体形式|执行情况)', text)  # 处罚内容
            Penalty_content = ''.join(Penalty_content[0][1])
            penalty_unit = '辽宁省环保厅'  # 处罚单位

            # 处罚金额
            if '罚款' in Penalty_content:
                Penalty_amount = re.findall('(罚款（人民币）：)(.*?)(元)', Penalty_content)[0][1]
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
