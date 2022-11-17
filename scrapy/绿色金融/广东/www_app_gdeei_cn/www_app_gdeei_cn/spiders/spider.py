
import scrapy
from www_app_gdeei_cn.data_process import *
from www_app_gdeei_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    condition = True

    def start_requests(self):
        for page in range(1, 35):
            url = f'https://www-app.gdeei.cn/gdeepub/data/punish?punishCompany=&punishFileno=&punishOrg=&page={page}'
            if self.condition is True:
                yield scrapy.Request(url=url, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        item = {}
        Penalty_doc_num = response.xpath("//table[@class='list']/tbody/tr/td[2]/a/text()").getall()
        Company_name = response.xpath("//div[@id='datatable']/table[@class='list']/tbody/tr/td[3]/text()").getall()
        penalty_unit = response.xpath("//div[@id='datatable']/table[@class='list']/tbody/tr/td[5]/text()").getall()
        Penalty_date = response.xpath("//div[@id='datatable']/table[@class='list']/tbody/tr/td[6]/text()").getall()
        Penalty_content = response.xpath("//div[@id='datatable']/table[@class='list']/tbody/tr/td[4]/text()").getall()
        for i in range(len(Company_name)):
            Offences = Penalty_content[i].split('；')[0]
            if '依据' in Penalty_content[i]:
                Punishment_basis = re.findall('(依据)(.*?)(第)', Penalty_content[i])
                Punishment_basis = ''.join(Punishment_basis[0][1])
            else:
                Punishment_basis = Penalty_content[i]
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)
            if '罚款' in Penalty_content[i]:  # 处罚金额
                Penalty_amount = re.findall('(罚款：)(.*?)(元)', Penalty_content[i])[0][1]
                Penalty_amount = Penalty_amount.replace('：', '')
                if include_number(Penalty_amount) and '万' in Penalty_amount:
                    Penalty_amount = float(Penalty_amount.replace('万', '').replace('罚款', '').replace('；', ''))*10000
            else:
                Penalty_amount = None

            item['Penalty_date'] = Penalty_date[i]
            item['Penalty_doc_num'] = Penalty_doc_num[i]
            item['penalty_unit'] = penalty_unit[i]
            item['Company_name'] = Company_name[i]
            item['Offences'] = Offences
            item['Punishment_basis'] = Punishment_basis
            item['Penalty_content'] = Penalty_content[i]
            item['Penalty_amount'] = Penalty_amount
            item['pageurl'] = md5(response.url + Penalty_date[i] + Penalty_doc_num[i])
            conn = redis_conn()
            result = conn.find_data(value=item['pageurl'])
            if result is False:
                yield item
            else:
                print('已存在:', item['pageurl'])
                self.condition = False


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
