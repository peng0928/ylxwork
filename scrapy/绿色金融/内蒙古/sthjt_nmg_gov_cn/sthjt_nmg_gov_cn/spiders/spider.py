import scrapy
from sthjt_nmg_gov_cn.data_process import *
from sthjt_nmg_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'nmgspider'
    start_urls = ['https://sthjt.nmg.gov.cn/xxgk/cfxx/index.html']
    condition = True

    def start_requests(self):
        for page in range(0, 12):
            if page > 0:
                lurl = self.start_urls[0].replace('index', f'index_{page}')
            else:
                lurl = self.start_urls[0]

            if self.condition is True:
                yield scrapy.Request(url=lurl, callback=self.lparse)
            else:
                break
                # pass

    def lparse(self, response):
        lresult = response.xpath("//div[@class='lanMu_con']//li/a")
        for query in lresult:
            lurl = 'https://sthjt.nmg.gov.cn/xxgk/cfxx' + query.xpath('.//@href').get()[1:]

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
            content = cresult.xpath("//div[@id='zoomfont']", character=False)

            if '无处罚' == content or '无处罚案件' in content or '无任何案件' in content or '本季度无行政处罚案件' in content or '无' == content or '无案件' == content or '无案件。' == content or '无行政处罚案件。' == content:
                pass
            else:
                if '强制执行。' in content:
                    Penalty_date = re.findall('(强制执行。)(.*)', content)[0][1]  # 处罚日期
                    Penalty_date = process_date(Penalty_date)  # 处罚日期
                    if Penalty_date is None:
                        Penalty_date = cresult.dpath("//div[@class='xlBtnLeft']")
                else:
                    Penalty_date = cresult.dpath("//div[@class='xlBtnLeft']")

                Penalty_doc_num = '内环' + re.findall('内环(.*?)号', content)[0] + '号'  # 处罚文书号
                Company_name = re.findall('号(.*?)：', content)[0]  # 单位名称
                Offences = re.findall('环境违法行为：(.*?)以上事实', content)[0]  # 违法事由

                # 处罚依据
                Punishment_basis = re.findall('(\.依据|我厅依据|为证。依据|规定。依据|行为，依据|你单位上述行为违反了)(.*?)(（|第|规定)', content)
                Punishment_basis = ''.join(Punishment_basis[0][1])
                Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
                Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
                Punishment_basis = ','.join(Punishment_basis)

                Penalty_content = re.findall('(并决定对你处以|并决定对你公司处以|我厅拟对你单位|我厅将对你单位|我厅决定|如下行政处罚：)(.*?)(限你单位|依据|限你自接|限于接到本处罚|你单位如对本决定不服)', content)  # 处罚内容
                Penalty_content = ''.join(Penalty_content[0][1])
                penalty_unit = '内蒙古自治区生态环境厅'  # 处罚单位

                # 处罚金额
                if '罚款' in Penalty_content:
                    Penalty_amount = re.findall('(人民币)(.*?)(元)', Penalty_content)[0][1]
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
                # yield item
                print(item)
        except Exception as e:
            print(e)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name} '.split())
