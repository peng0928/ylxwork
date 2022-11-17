# 安徽
import scrapy
from sthj_shandong_gov_cn.data_process import *
from sthj_shandong_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'shspider'
    condition = True

    def start_requests(self):
        url = [
            'http://sthj.shandong.gov.cn/hjjc/xzcf/index.html',
            'http://sthj.shandong.gov.cn/hjjc/xzcf/index_1.html',
            'http://sthj.shandong.gov.cn/hjjc/xzcf/index_2.html',
        ]
        for lurl in url:
            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        lresult = response.xpath("//td//a")
        for query in lresult:
            title = query.xpath('.//text()').get()
            if '行政处罚决定书' in title:
                lurl = 'http://sthj.shandong.gov.cn/hjjc/xzcf' + query.xpath('.//@href').get()[1:]

                conn = redis_conn()
                result = conn.find_data(value=1)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    print('已存在:', lurl)
                    self.condition = False

    def cparse(self, response):

        item = {}
        cresult = Xpath(response.text)
        content = cresult.xpath("//td[@class='zw_new']", character=False)
        Penalty_date = re.findall('(强制执行。山东省生态环境厅|强制执行。)(.*)', content)  # 处罚日期
        if '年' in Penalty_date[0][1]:
            Penalty_date = cnnum2albnum(Penalty_date[0][1])
            Penalty_date = process_date(Penalty_date)  # 处罚日期
        else:
            Penalty_date = process_date(Penalty_date[0][1])  # 处罚日期

        Penalty_doc_num = '鲁环' + re.findall('鲁环(.*?)号', content)[0] + '号'  # 处罚文书号
        Company_name = re.findall('(当事人名称：|被处罚单位名称：)(.*?)(身份证|营业执照注册号|社会信用代码)', content)[0][1]  # 单位名称
        Offences = re.findall('(一、主要违法事实和证据|违法行为：)(.*?)(你公司的上述行为|你公司超标排污|以上违法|以上事实)', content)[0][1]  # 违法事由

        # 处罚依据
        Punishment_basis = re.findall('(期限根据|，依据|期限依据|。依据)(.*?)(我厅)', content)
        Punishment_basis = ''.join(Punishment_basis[0][1])
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        Penalty_content = re.findall('(我厅现对你单位|规定，我厅|我厅决定|的违法行为，)(.*?)(根据)', content)  # 处罚内容
        Penalty_content = [i[1] for i in Penalty_content]
        Penalty_content = ','.join(Penalty_content)
        penalty_unit = '山东省生态环境厅'  # 处罚单位

        # 处罚金额
        if '罚款' in Penalty_content:
            Penalty_list = []
            patten = ('元，并处|如下处罚：处|改正，处以|2、处|3、处|（二）罚款|罚款，即|；处以|，即处以|即人民币|对你公司处|对你单位罚款|对你处以罚款|对你罚款|对你单位处以罚款')
            Penalty_words = re.sub(patten, '开始罚罚', Penalty_content)
            Penalty_word = re.findall('开始罚罚(.*?)元', Penalty_words)

            for i in Penalty_word:
                if '开始罚罚' in i:
                    i = i.split('开始罚罚')[-1]
                else:
                    i = i
                Penalty_amount = i.replace('人民币', '').replace('以', '').replace('罚款', '').replace('处', '')
                if include_number(Penalty_amount):
                    if '万' in Penalty_amount:
                        Penalty_amount = float(Penalty_amount.replace('万', '')) * 10000
                    else:
                        Penalty_amount = Penalty_amount
                else:
                    Penalty_amount = chinese2digits(Penalty_amount)
                Penalty_list.append(str(Penalty_amount))
            Penalty_amount = ','.join(Penalty_list)
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
        # yield item
        print(response.url, item)


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
