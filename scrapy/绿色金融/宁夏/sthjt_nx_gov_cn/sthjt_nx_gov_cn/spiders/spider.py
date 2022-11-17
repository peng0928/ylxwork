import scrapy, re
from sthjt_nx_gov_cn.data_process import *
from sthjt_nx_gov_cn.redis_conn import *
from fake_useragent import UserAgent


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [406, 301],
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'en',
            'user-agent': UserAgent().random}
    }
    start_urls = [
        'https://sthjt.nx.gov.cn//portal/news/getReleasedNewsListByCatagory.do'
    ]
    condition = True

    def start_requests(self):
        for page in range(1, 6):
            body = f'catagory=180&pageNum={page}&pageSize=10&title=&startTime=&endTime='
            lurl = self.start_urls[0]
            if self.condition is True:
                yield scrapy.Request(url=lurl, body=body, method='POST', callback=self.lparse, dont_filter=True)
            else:
                break

    def lparse(self, response):
        ljson = response.json().get('data', None).get('list', None)
        for query in ljson:
            title = query.get('title', None)
            if '行政处罚决定书' in title:
                lurl = 'https://sthjt.nx.gov.cn/page/' + query.get('newsHtmlUrl', None)

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    print('已存在:', lurl)
                    # self.condition = False

    def cparse(self, response):
        try:
            item = {}
            cresult = Xpath(response.text)
            title = cresult.xpath("//h2[@id='XWXQTitle']")
            content = cresult.xpath("//div[@id='XWXQContent']|//div[@class='news_content_word']", character=False)

            Penalty_date = re.findall('(强制执行。)(.*)', content)[0][1]  # 处罚日期
            Penalty_date = process_date(Penalty_date)  # 处罚日期

            if '（' in title:
                Penalty_doc_num = re.findall('（(.*?)）', title)[0]  # 处罚文书号
            else:
                Penalty_doc_num = '宁环罚' + re.findall('宁环罚(.*?)号', content)[0] + '号'  # 处罚文书号

            Company_name = re.findall('(.*?)(（统一|（公司|\(统一)', content)[0][0]  # 单位名称
            if '号' in Company_name:
                Company_name = Company_name.split('号')[-1]
            Company_name = Company_name.replace('：', '')

            Offences = re.findall('(违法行为：|复印件的函》，)(.*?)以上事实', content)[0][1]  # 违法事由

            Punishment_basis = re.findall('(原则，依据|行为属于|。根据|。依据)(.*?)第', content)[0][1]  # 处罚依据
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            Penalty_content = re.findall('(如下行政处罚：|作出以下处理决定：)(.*?)(限你公司接到|限于接到本处罚)', content)[0][1]  # 处罚内容
            penalty_unit = '宁夏回族自治区生态环境厅'  # 处罚单位

            # 处罚金额
            if '罚款' in Penalty_content:
                if '合计' in Penalty_content:
                    Penalty_amount = re.findall('(合计罚款)(.*?)(元)', Penalty_content)[0][1]
                else:
                    Penalty_amount = re.findall('(罚款)(.*?)(元)', Penalty_content)[0][1]
                Penalty_amount = numtohans(Penalty_amount.replace('人民币', '').replace('：', ''))
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
        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
