import scrapy
from sthjt_yn_gov_cn.data_process import *
from sthjt_yn_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['http://sthjt.yn.gov.cn/hjjc/hjjcxzcf/index_1.html']
    condition = True

    def start_requests(self):
        for page in range(0, 13):
            if page > 0:
                url = f'http://sthjt.yn.gov.cn/hjjc/hjjcxzcf/index_{page}.html'
            else:
                url = 'http://sthjt.yn.gov.cn/hjjc/hjjcxzcf/index.html'

            if self.condition is True:
                yield scrapy.Request(url, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        lresult = response.xpath("//div[@class='data-list']//a")
        for query in lresult:
            title = query.xpath('.//text()').get()
            if '行政处罚决定书' in title:
                lurl = 'http://sthjt.yn.gov.cn/hjjc/hjjcxzcf' + query.xpath('.//@href').get()[1:]

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    if '.pdf' in lurl:
                        pass
                    else:
                        yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    print('已存在:', lurl)
                    self.condition = False

    # 津市环罚字
    def cparse(self, response):
        creslut = Xpath(response.text)
        item = {}
        title = creslut.xpath("//div[@class='content-title']")
        content = creslut.xpath("//div[@class='content-box']/div[@id='Zoom']", filter='script|style', character=False)
        print(content)
        # 处罚日期
        Penalty_date = re.findall('(制执行。|维西傈僳族自治县环境保护局)(.*)', content)
        Penalty_date = process_date(Penalty_date[0][1])

        # 处罚文书号
        try:
            Penalty_doc_num = '云环罚' + re.findall('云环罚(.*)', title)[0]
        except:
            Penalty_doc_num = '云环罚' + re.findall('云环罚(.*?)号', content)[0] + '号'

        # 单位名称
        try:
            Company_name = creslut.xpath("//div[@class='content-title']")
            Company_name = re.findall('(（|\()(.*?)(）|\))', Company_name)[0][1]
        except:
            Company_name = re.findall('号(.*?)：', content)[0]
        Company_name = Company_name.replace('法定代表人', '').replace('晋宁段', '晋宁段）指挥部）').replace('法人代表', '')
        # 违法事由
        Offences = re.findall('(一、环境违法事实和证据|存在以下环境违法行为：|实施了以下环境违法行为：)(.*?)(以上行为违反了|上述行为违反了|以上事实)', content)[0][1]
        if '发现你单位实施了以下环境违法行为：' in Offences:
            Offences = re.findall('(发现你单位实施了以下环境违法行为：)(.*)', Offences)[0][1]

        # 处罚依据
        Punishment_basis = re.findall('(上述行为违反了|权利。根据|违法行为时适用的|依据、种类|采纳。根据|种类、依据)(.*?)第', content)[0][1]
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《"+i+"》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        # 处罚内容
        Penalty_content = re.findall('(进行处罚，决定：|责令你公司|如下行政处罚决定：|作出如下处理：|如下行政处罚：|如下处罚决定：|如下处理决定：)(.*?)(三、|限于接到本处罚决定之日)', content)[0][1]

        #处罚金额
        if '罚款' in Penalty_content:
            Penalty_amount = re.findall('(罚款)(.*?)(元|（)', Penalty_content)[0][1].replace('人民币', '')
            Penalty_amount = chinese2digits(Penalty_amount)
        else:
            Penalty_amount = None

        # 处罚单位
        penalty_unit = '云南省环境保护厅'

        item['Penalty_date'] = Penalty_date
        item['Penalty_doc_num'] = Penalty_doc_num
        item['Company_name'] = Company_name
        item['Offences'] = Offences
        item['Punishment_basis'] = Punishment_basis
        item['Penalty_content'] = Penalty_content
        item['penalty_unit'] = penalty_unit
        item['Penalty_amount'] = Penalty_amount
        item['pageurl'] = response.url
        yield item
        # print(item)



############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name} -o test.json'.split())