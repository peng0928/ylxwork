import scrapy, re, os
from sthjt_hunan_gov_cn.data_process import *
from sthjt_hunan_gov_cn.redis_conn import *
from fake_useragent import UserAgent


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'user-agent': UserAgent().random}
    }
    start_urls = ['http://sthjt.hunan.gov.cn/sthjt/xxgk/zdly/jdzf/ajcc/index.html']
    condition = True

    def start_requests(self):
        for page in range(1, 6):
            if page > 1:
                lurl = self.start_urls[0].replace('index', f'index_{page}')
            else:
                lurl = self.start_urls[0]

            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse)
            else:
                break

    def lparse(self, response):
        urls = response.xpath("//div[@class='hy-list-text']/ul/li/a")
        for query in urls:
            title = query.xpath('.//text()').get()
            if '处罚决定书' in title:
                lurl = 'http://sthjt.hunan.gov.cn' + query.xpath('.//@href').get()
                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    print('已存在:', lurl)
                    self.condition = False

    def cparse(self, response):
        # try:
        item = {}
        cresult = Xpath(response.text)
        content = cresult.xpath("//div[@id='j-show-body']", filter='style|script', character=False)
        file = cresult.xpath("//div[@id='j-show-body']//a")
        if file and 'doc' in file:
            print(file)
        elif file and 'pdf' in file:
            print(file)
        elif file and 'PDF' in file:
            print(file)
        else:
            print(content)
            Penalty_date = re.findall('(强制执行。湖南省环境保护厅|湖湖南省环境保护厅)(.*)', content)[0][1]  # 处罚日期
            Penalty_date = process_date(Penalty_date)  # 处罚日期

            Penalty_doc_num = cresult.xpath("//div[@class='main_content']/h2")
            Penalty_doc_num = re.findall('处罚决定书(.*)', Penalty_doc_num)[0]  # 处罚文书号

            Company_name = re.findall('(.*?)(:法定代表人|：营业执照注册号|:营业执照注册号|:统一社会信用代码|:组织机构代码)', content)[0][0]  # 单位名称
            if '行政处罚决定书' in Company_name:
                Company_name = re.findall('行政处罚决定书(.*)', Company_name)[0]
            Offences = re.findall('(整治现场执法时，|环境违法行为：|我厅调查发现,|违法事实和证据)(.*?)(你单位的上述行为|我厅已委托|以上事实)', content)[0][1]  # 违法事由

            # 处罚依据
            Punishment_basis = re.findall('(处理。依据|我厅依据|我厅根据|期限依据|为证。依据)(.*?)第', content)[0][1]
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            Penalty_content = re.findall('(以下处理：|如下行政处罚：|行政处罚:|实施以下处罚：)(.*?)(限于接到本处罚|你单位应于接)', content)[0][1]  # 处罚内容
            penalty_unit = '湖南省环境保护厅'  # 处罚单位

            # 处罚金额
            if '罚款' in Penalty_content:
                Penalty_amount = re.findall('(罚款)(.*?)(元)', Penalty_content)[0][1]
                Penalty_amount = numtohans(Penalty_amount.replace('人民币', ''))
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
            # print(item)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name} -o test.json'.split())
