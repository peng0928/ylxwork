import scrapy
from sthj_tj_gov_cn.data_process import *
from sthj_tj_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['https://sthj.tj.gov.cn/ZWGK4828/ZFXXGK8438/FDZDGK27/XZCFQZXZCFXX7581/index.html']
    condition = True

    def start_requests(self):
        for page in range(0, 50):
            if page > 0:
                url = f'https://sthj.tj.gov.cn/ZWGK4828/ZFXXGK8438/FDZDGK27/XZCFQZXZCFXX7581/index_{page}.html'
            else:
                url = 'https://sthj.tj.gov.cn/ZWGK4828/ZFXXGK8438/FDZDGK27/XZCFQZXZCFXX7581/index.html'
            if self.condition is True:
                yield scrapy.Request(url, callback=self.lparse)

            else:
                break

    def lparse(self, response):
        lresult = response.xpath("//div[@class='xl-right-content']//a/@href").getall()
        titles = response.xpath("//div[@class='xl-right-content']//a/text()").getall()
        for item in range(len(lresult)):
            url = 'https://sthj.tj.gov.cn/ZWGK4828/ZFXXGK8438/FDZDGK27/XZCFQZXZCFXX7581' + lresult[item][1:]
            if './../../' in lresult[item][1:]:
                lurl = 'https://sthj.tj.gov.cn/ZWGK4828' + lresult[item][1:].replace('./../../', '/')
            else:
                lurl = url
            conn = redis_conn()
            result = conn.find_data(value=lurl)

            if result is False:
                title = ''.join(titles[item]).replace(' ', '')
                if '环罚字' in title:
                    data = title.split('环罚字')
                    Company_name = data[0].replace('\u2002', '').replace('津市', '')
                    Penalty_doc_num = '津市环罚字' + data[1]
                    yield scrapy.Request(lurl, callback=self.cparse, meta={'Penalty_doc_num': Penalty_doc_num, 'Company_name': Company_name})

                if '处罚决定书' in title or '违法行为决定书' in title:
                    data = title.split('决定书')
                    Penalty_doc_num = '津市环罚字' + data[1]
                    yield scrapy.Request(lurl, callback=self.Decision, body=response.body, meta={'Penalty_doc_num': Penalty_doc_num})
            else:
                print('已存在:', lurl)
                self.condition = False

    # 津市环罚字
    def cparse(self, response):
        try:
            creslut = Xpath(response.text)
            item = {}
            content = creslut.xpath("//div[@id='xlrllt']|//div[@id='zoom']", character=False)

            # 处罚日期
            Penalty_date = re.compile('(制执行|制执行。|特此公告。)(\d+年\d{1,2}月\d{1,2}日)(注：|附件：)*')
            try:
                Penalty_date = Penalty_date.findall(content)[0][1].replace('年', '-').replace('月', '-').replace('日', '')
            except:
                Penalty_date = creslut.dpath("//meta[@name='PubDate']/@content|//div[@class='xw-xtitle clear']")

            # 处罚文书号
            Penalty_doc_num = response.meta['Penalty_doc_num']

            # 单位名称
            Company_name = response.meta['Company_name']
            if '公司' not in Company_name:
                Company_name = Company_name.replace('公', '公司')

            # 违法事由
            Offences = re.findall('(及采纳情况)(.*?)以上事实，', content)[0][1]
            if '发现你单位实施了以下环境违法行为：' in Offences:
                Offences = re.findall('(发现你单位实施了以下环境违法行为：)(.*)', Offences)[0][1]

            # 处罚依据
            Punishment_basis = re.findall('(依据、种类)(.*?)三、', content)[0][1]
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《"+i+"》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            # 处罚内容
            Penalty_content = re.findall('(二、行政处罚.*?规定|二、责令.*?规定|二、责令.*?项，)(.*?)三、', content)[0][1]
            Penalty_content = Penalty_content.replace('：', '').replace(':', '').replace('，责令', '').replace('我局', '')
            if Penalty_content[0] == '，':
                Penalty_content = Penalty_content[1:]

            #处罚金额
            if '处罚款' in Penalty_content or '处人民币' in Penalty_content:
                Penalty_amount = re.findall('(处罚款|处人民币)(.*?)(元)', Penalty_content)[0][1]
                try:
                    Penalty_amount = re.findall('\d+', Penalty_amount)[0]
                except:
                    Penalty_amount = chinese2digits(Penalty_amount)
            else:
                Penalty_amount = None

            # 处罚单位
            penalty_unit = '天津市环境保护局'

            item['Penalty_date'] = Penalty_date
            item['Penalty_doc_num'] = Penalty_doc_num
            item['Company_name'] = Company_name
            item['Offences'] = Offences
            item['Punishment_basis'] = Punishment_basis
            item['Penalty_content'] = Penalty_content
            item['penalty_unit'] = penalty_unit
            item['Penalty_amount'] = Penalty_amount
            item['pageurl'] = response.url
            # yield item
            yield item
        except Exception as e:
            print(e)

    # 决定书
    def Decision(self, response):
        try:
            creslut = Xpath(response.text)
            item = {}
            content = creslut.xpath("//div[@id='xlrllt']|//div[@id='zoom']", character=False)

            # 单位名称
            Company_name = re.findall('号(.*?)(：|企业法|组织|事业单位)', content)[0][0]

            # 处罚日期
            Penalty_date = re.compile('(制执行。|政诉讼。)(.*)')
            Penalty_date = Penalty_date.findall(content)[0][1]
            Penalty_date = process_date(Penalty_date)

            # 处罚文书号
            Penalty_doc_num = response.meta['Penalty_doc_num']

            # 违法事由
            Offences = re.findall('(及采纳情况|环境违法事实和证据)(.*?)以上事实', content)[0][1]
            if '发现你单位实施了以下环境违法行为：' in Offences or '发现你单位' in Offences or '检查，发现' in Offences:
                Offences = re.findall('(发现你单位实施了以下环境违法行为：|发现你单位|检查，发现)(.*)', Offences)[0][1]

            # 处罚依据
            Punishment_basis = re.findall('(种类依据|依据、种类)(.*?)三、', content)[0][1]
            Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
            Punishment_basis = ["《"+i+"》" for i in Punishment_basis]
            Punishment_basis = ','.join(Punishment_basis)

            # 处罚内容
            Penalty_content = re.findall('(我局决定)(.*?)三、', content)[0][1]

            # 处罚单位
            penalty_unit = '天津市环境保护局'

            #处罚金额
            if '处罚款' in Penalty_content:
                Penalty_amount = re.findall('(处罚款)(.*?)(元)', Penalty_content)[0][1]
                try:
                    Penalty_amount = re.findall('\d+', Penalty_amount)[0]
                except:
                    Penalty_amount = chinese2digits(Penalty_amount)
            else:
                Penalty_amount = None

            item['Penalty_date'] = Penalty_date
            item['Penalty_doc_num'] = Penalty_doc_num
            item['Company_name'] = Company_name
            item['Offences'] = Offences
            item['Punishment_basis'] = Punishment_basis
            item['Penalty_content'] = Penalty_content
            item['penalty_unit'] = penalty_unit
            item['Penalty_amount'] = Penalty_amount
            item['pageurl'] = response.url

            # print(response.url, Company_name)
            # yield item
            yield item
        except Exception as e:
            print(e)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())