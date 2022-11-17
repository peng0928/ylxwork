# 安徽
import scrapy
from sthjt_sc_gov_cn.data_process import *
from sthjt_sc_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'ahspider'
    condition = True

    def start_requests(self):
        url = 'http://sthjt.sc.gov.cn/sthjt/c100456/zfxxgk_gknrz.shtml'
        if self.condition is True:
            yield scrapy.Request(url=url, callback=self.lparse)

    def lparse(self, response):
        lresult = response.xpath("//div[@id='wzlm']/dl/dd/a")
        for query in lresult:
            lurl = 'http://sthjt.sc.gov.cn' + query.xpath('.//@href').get()

            conn = redis_conn()
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, callback=self.cparse)
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        try:
            item, penalty_dict = {}, {}
            name = response.xpath("//div[@class='TRS_Editor']//tr[position()>1]/td[1]")
            value = response.xpath("//div[@class='TRS_Editor']//tr[position()>1]/td[2]")
            for query in range(len(name)):
                name_text = name[query].xpath('.//text()').getall()
                value_text = value[query].xpath('.//text()').getall()
                if name_text is None or value_text is None:
                    pass
                else:
                    name_text = process_text(name_text, character=False)
                    value_text = process_text(value_text, character=False)
                    penalty_dict[name_text] = value_text

            Penalty_date = penalty_dict['处罚决定日期']  # 处罚日期
            Penalty_doc_num = penalty_dict['行政处罚决定书文号']  # 处罚文号
            Company_name = penalty_dict['行政相对人名称']  # 单位名称
            Offences = penalty_dict['违法事实']  # 违法事由

            # 处罚依据
            Punishment_basis = penalty_dict['处罚依据']
            Punishment_basis = re.findall('(.*?)(第)', Punishment_basis)[0][0]
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            Penalty_content = penalty_dict['处罚内容']  # 处罚内容
            penalty_unit = '四川省生态环境厅'  # 处罚单位

            # 处罚金额
            if '罚款' in Penalty_content:
                Penalty_amount = re.findall('(罚款)(.*?)(元)', Penalty_content)[0][1]
                Penalty_amount = chinese2digits(Penalty_amount, fl=True)
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
