# 安徽
import scrapy
from sthjt_ah_gov_cn.data_process import *
from sthjt_ah_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'ahspider'
    condition = True
    def start_requests(self):
        for page in range(1, 10):
            url = f'https://sthjt.ah.gov.cn/site/label/8888?labelName=publicInfoList&siteId=6788031&pageSize=15&pageIndex={page}&action=list&fuzzySearch=false&fromCode=title&keyWords=&sortType=1&isDate=true&dateFormat=yyyy-MM-dd&length=80&organId=21691&type=4&catIds=&cId=&result=%E6%9A%82%E6%97%A0%E7%9B%B8%E5%85%B3%E4%BF%A1%E6%81%AF&file=%2Fxxgk%2FpublicInfoList_newest2020&catId=32710021'

            if self.condition is True:
                yield scrapy.Request(url=url, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        lresult = response.xpath("//a[@class='title']")
        for query in lresult:
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
        try:
            item = {}
            cresult = Xpath(response.text)
            content = cresult.xpath("//div[@class='j-fontContent newscontnet minh500']", character=False)
            Penalty_date = re.findall('(诉讼。安徽省生态环境厅|强制执行。)(.*)', content)  # 处罚日期
            if len(Penalty_date) > 0:
                Penalty_date = process_date(Penalty_date[0][1])  # 处罚日期
            else:
                Penalty_date = cresult.dpath("//div[@class='xlBtnLeft']")

            Penalty_doc_num = cresult.xpath("//tbody/tr[4]/td[@id='_fileNum']")
            if Penalty_doc_num is None:
                Penalty_doc_num = re.findall('安徽省生态环境厅(.*?)行政处罚决定书', content)[0]  # 处罚文书号
            Company_name = re.findall('(安徽省生态环境厅行政处罚决定书|行政处罚决定书)(.*?)(：公民身份证号码|：统一社会信用代码)', content)[0][1]  # 单位名称
            Offences = re.findall('(环境违法行为：|环境违法事实和证据)(.*?)(你公司上述行为违反了|以上事实)', content)[0][1]  # 违法事由

            # 处罚依据
            Punishment_basis = re.findall('(上述行为违反了|申辩。依据)(.*?)(我厅决定|规定。)', content)
            Punishment_basis = ''.join(Punishment_basis[0][1])
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            Penalty_content = re.findall('(作出如下行政处罚：|非道路移动机械行为，)(.*?)(三、行政处罚决定|你公司如不服本处罚决定|你如不服本处罚决定)', content)  # 处罚内容
            Penalty_content = ''.join(Penalty_content[0][1])
            penalty_unit = '安徽省生态环境厅'  # 处罚单位

            # 处罚金额
            if '罚款' in Penalty_content:
                Penalty_amount = re.findall('(合计)(.*?)(元)', Penalty_content)[0][1]
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
            # print(item)

        except Exception as e:
            print(e)

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
