# -*- coding: utf-8 -*-
# @Date    : 2022-08-24
# @Author  : chenxuepeng
# href  : https://sthj.sh.gov.cn/hbzhywpt1060/hbzhywpt1061/index.html
import scrapy, requests
from sthj_sh_gov_cn.data_process import *
from sthj_sh_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'nmgspider'
    start_urls = ['https://link.sthj.sh.gov.cn/sh/xzcf/law_enforce_list.jsp']
    condition = True

    def start_requests(self):
        for page in range(1, 5):
            body = f'schCompany=&schPunishReason=&pageNo={page}'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            lurl = self.start_urls[0]
            if self.condition is True:
                yield scrapy.Request(url=lurl, headers=headers, body=body, method='POST', callback=self.lparse)
            else:
                break
                # pass

    def lparse(self, response):
        lresult = response.xpath("//div[@class='bd']/ul/li/a/@href").getall()
        for query in lresult:
            lurl = 'https://link.sthj.sh.gov.cn/sh/xzcf/' + query
            conn = redis_conn()
            result = conn.find_data(value=lurl)
            if result is False:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                resp = requests.get(lurl, headers=headers)
                page = Xpath(resp.text)
                page = page.xpath("//td[3]", character=False)
                page = re.findall('共(\d+)页', page)[0]
                for i in range(1, int(page)):
                    data = f'pageNo={i}'
                    yield scrapy.Request(url=lurl, headers=headers, method='POST', body=data, callback=self.cparse)
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        try:
            item = {}
            cresult = Xpath(response.text)
            Penalty_dates = cresult.xpath("//tr[starts-with(@class,'bgCol')]//td[5]", is_list=True)
            Company_names = cresult.xpath("//td[2]/@title", is_list=True)  # 单位名称
            Offences = cresult.xpath("//tr[starts-with(@class,'bgCol')]/td[4]/@title", is_list=True)  # 违法事由
            Punishment_basis = cresult.xpath("//tr[starts-with(@class,'bgCol')]/td[3]/@title", is_list=True)  # 处罚依据
            Penalty_contents = cresult.xpath("//tr[starts-with(@class,'bgCol')]//tr[1]/td", is_list=True, easy=True)  # 处罚内容
            penalty_units = cresult.xpath("//tr[starts-with(@class,'bgCol')]//tr[2]/td", is_list=True, easy=True)  # 处罚内容

            # 处罚金额
            for i in range(len(Penalty_dates)):
                Penalty_date = Penalty_dates[i]
                penalty_unit = penalty_units[i]
                Company_name = Company_names[i]
                Offence = Offences[i]
                Punishment_basi = Punishment_basis[i]
                Penalty_content = Penalty_contents[i]

                item['Penalty_date'] = timechange(Penalty_date)
                item['Penalty_doc_num'] = None
                item['penalty_unit'] = penalty_unit
                item['Company_name'] = Company_name
                item['Offences'] = Offence
                item['Punishment_basis'] = Punishment_basi
                item['Penalty_content'] = Penalty_content
                item['Penalty_amount'] = None
                item['pageurl'] = response.url
                yield item
                # print(item)
        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
