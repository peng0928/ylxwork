import scrapy, asyncio
from sthjt_shanxi_gov_cn.data_process import *
from sthjt_shanxi_gov_cn.redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = [
        # 核辐射行政处罚
        'http://sthjt.shanxi.gov.cn/wryjg/xzcf/hfsxzcf/index.shtml',

        # 行政处罚决定,
        'http://sthjt.shanxi.gov.cn/wryjg/xzcf/xzcfjd/index.shtml'
    ]
    start_pages = [5, 14]
    # start_pages = [5, 5]
    condition = {'condition': True}

    def start_requests(self):
        for i in range(2):
            self.condition = {'condition': True}
            for page in range(self.start_pages[i]):
                if page > 0:
                    lurl = self.start_urls[i].replace('index', f'index_{page}')
                else:
                    lurl = self.start_urls[i]

                if self.condition['condition'] is True:
                    yield scrapy.Request(url=lurl, callback=self.lparse)
                else:
                    print('已存在', lurl)
                    break

    def lparse(self, response):

        lresult = response.xpath("//div[@class='list-details-bar']/ul[@class='list-details']/li/a")
        for query in lresult:
            title = query.xpath(".//text()").get().strip()
            if '晋环' in title:
                lurl = query.xpath(".//@href").get().strip()
                lurl = '/'.join(response.url.split('/')[:-1]) + lurl[1:]

                conn = redis_conn()
                # result = conn.find_data(value=lurl)
                result = conn.find_data(value=1)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.cparse)
                else:
                    self.condition['condition'] = False

    def cparse(self, response):

        item = {}
        cresult = Xpath(response.text)
        content = cresult.xpath("//div[@class='text-details']", character=False)

        if '强制执行。' in content:
            try:
                Penalty_date = re.findall('(强制执行。)(.*)', content)  # 处罚日期
                Penalty_date = process_date(Penalty_date[0][1])  # 处罚日期
            except:
                Penalty_date = cresult.dpath("//p[@class='td-title-2']")
        else:
            Penalty_date = cresult.dpath("//p[@class='td-title-2']")

        Penalty_doc_num = '晋环' + re.findall('晋环(.*?)号', content)[0] + '号'  # 处罚文书号
        Company_name = re.findall('(号行政处罚决定书)(.*?)：', content)  # 单位名称
        if Company_name:
            Company_name = Company_name[0][1]
        else:
            Company_name = re.findall('编辑时间：\d{4}-\d{1,2}-\d{1,2}(.*?)：', content)[0]


        Offences = re.findall('(违法行为：|违法事实：|询时核实：)(.*?)(以上事实)', content)  # 违法事由
        if Offences:
            Offences = Offences[0][1]
        else:
            Offences = re.findall('(申辩\(听证\)及采纳情况|违法行为：|违法事实：|询时核实：)(.*?)(你公司的上述行为违反了|你单位的上述行为违反了)', content)[0][1]  # 违法事由

        # 处罚依据
        Punishment_basis = re.findall('(采纳。依据|处理。依据|规定。依据|依据、种类|申请。依据)(.*?)(三、|行政处罚：)', content)[0][1]
        Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        Punishment_basis = ','.join(Punishment_basis)

        if '限于接到处罚决定书' in content:
            Penalty_content = re.findall('(我厅决定对你公司|我厅决定对你单位|我厅责令你单位|根据上述规定，我厅决定对你单位|下行政处罚：|下行政处罚:)(.*?)(限于接到处罚决定书)', content)[0][1]  # 处罚内容
        else:
            Penalty_content = re.findall('(我厅决定对你公司|我厅决定对你单位|我厅责令你单位|根据上述规定，我厅决定对你单位|下行政处罚：)(.*?)(根据《中华人民共和国行政处罚法》|三、|限于接到本处罚决定)', content)[0][1]  # 处罚内容
        penalty_unit = '山西省环境保护厅'  # 处罚单位

        # 处罚金额
        if '罚款' in Penalty_content:
            Penalty_list = []
            patten = ('行为处以罚款|共处人民币|处以人民币|合并处以罚款|合计处以罚款|合并处罚|行政处罚：罚款|违法行为处以罚|事实处以罚款|行为罚款|行为，处以|并处罚款|运行，处|使用，处以|运行，罚款')
            Penalty_word = re.sub(patten, '开始处罚', Penalty_content)
            Penalty_word = re.findall('开始处罚(.*?)元', Penalty_word)
            for i in Penalty_word:
                Penalty_amount = i.replace('人民币', '').replace('以', '')
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
        yield item


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
