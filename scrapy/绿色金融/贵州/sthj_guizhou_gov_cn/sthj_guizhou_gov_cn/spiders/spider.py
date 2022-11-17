import scrapy, re
from sthj_guizhou_gov_cn.data_process import *
from sthj_guizhou_gov_cn.redis_conn import *
from fake_useragent import UserAgent


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [406, 301],
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'user-agent': UserAgent().random}
    }
    start_urls = ['https://sthj.guizhou.gov.cn/ywgz/zfjd/index.html']
    condition = True

    def start_requests(self):
        for page in range(5):
            if page > 0:
                lurl = self.start_urls[0].replace('index', f'index_{page}')
            else:
                lurl = self.start_urls[0]
            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse, dont_filter=True)
            else:
                break

    def lparse(self, response):
        urls = response.xpath("//div[@class='PageMainBox aBox']/ul/li/a")
        for query in urls:
            title = query.xpath('.//text()').get()
            if '行政处罚决定书' in title or '违法行为决定书' in title:
                lurl = query.xpath('.//@href').get()

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
        content = cresult.xpath("//div[@class='Article_Con aBox']", character=False, filter='style|script')

        Penalty_date = re.findall('(联系电话|强制执行。)(.*)', content)[0][1]  # 处罚日期
        Penalty_date = process_date(Penalty_date)  # 处罚日期
        Penalty_doc_num = re.findall('号(.*)(企业法人|营业执照)', content)[0][0].replace('：', '')  # 处罚文书号
        Company_name = re.findall('(.*?)(企业法人|营业执照)', content)[0][0]  # 单位名称
        if '号' in Company_name:
            Company_name = re.findall('号(.*)', Company_name)[0]

        Company_name = Company_name.replace(':', '').replace('：', '')
        Offences = re.findall('(进行现场检查，|一、环境违法事实与证据|环境违法行为：)(.*?)(上述事实|你公司上述行为违反了|以上事实)', content)[0][1]  # 违法事由

        # 处罚依据
        Punishment_basis = re.findall('(依据、种类|规定。依据)(.*?)(三、|现责令)', content)[0][1]
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        Penalty_content = re.findall('(整改情况，我厅决定|规定，现|根据上述规定，我厅决定|连续处罚：|实施以下处罚：)(.*?)(三、|我厅将对你公司改正违法行为的情况进行监督|根据《)', content)[0][1]  # 处罚内容
        penalty_unit = '贵州省环境保护厅'  # 处罚单位

        # 处罚金额
        if '罚款' in Penalty_content:
            Penalty_amount = re.findall('(公司处以|作出罚款|，即罚款)(.*?)(（|元)', Penalty_content)[0][1]
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


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
