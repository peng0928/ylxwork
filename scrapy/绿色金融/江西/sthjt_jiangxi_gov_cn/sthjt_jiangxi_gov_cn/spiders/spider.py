import scrapy, requests, os, office, pytesseract
from urllib.parse import urljoin
from sthjt_jiangxi_gov_cn.data_process import *
from PIL import Image

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = [
        'http://sthjt.jiangxi.gov.cn/module/web/jpage/dataproxy.jsp?startrecord=0&endrecord=300&perpage=100',
        'http://sthjt.jiangxi.gov.cn/module/web/jpage/dataproxy.jsp?startrecord=300&endrecord=520&perpage=100',
    ]

    def start_requests(self):
        body = 'col=1&webid=236&path=http%3A%2F%2Fsthjt.jiangxi.gov.cn%2F&columnid=42164&sourceContentType=1&unitid=380055&webname=%E6%B1%9F%E8%A5%BF%E7%9C%81%E7%94%9F%E6%80%81%E7%8E%AF%E5%A2%83%E5%8E%85&permissiontype=0'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for page in self.start_urls:
            yield scrapy.Request(url=page, body=body, headers=headers, method='POST', callback=self.parse)

    def parse(self, response, **kwargs):
        cresult = Xpath(response.text)
        title = cresult.xpath('//a', is_list=True)
        lurl = cresult.xpath('//a/@href', is_list=True)
        for item in range(len(title)):
            if '决定书' in title[item]:
                yield scrapy.Request(url=lurl[item], callback=self.cparse)

    def cparse(self, response):
        item = {}

        cresult = Xpath(response.text)
        file = cresult.fxpath("//div[@id='zoom']//a", rule='http://sthjt.jiangxi.gov.cn')
        filename = file[0]
        filelink = file[1]
        if '|' in filename:
            filelink = filelink.split('|')[-1]
        downname = filelink.split('filename=')[-1]
        os.makedirs('../file', exist_ok=True)
        filedocx_exists = os.path.exists(f'../file/{downname}')
        if filedocx_exists is False:
            fileresp = requests.get(filelink)
            f = open(f'../file/{downname}', 'wb')
            f.write(fileresp.content)
        pg_list = office.pdf.pdf2imgs(
            pdf_path='../file/' + downname,
            out_dir='../pdffile/' + downname
        )
        for img in pg_list:
            im = Image.open(f'../pdffile/{downname}/{img}')
            text = pytesseract.image_to_string(im, lang='chi_sim')
            print(text)
        # content = cresult.xpath("//div[@class='p_nei']/div[@id='BodyLabel']", character=False)
        #
        # Penalty_date = re.findall('(强制执行。)(.*)', content)[0][1]  # 处罚日期
        # Penalty_date = process_date(Penalty_date)  # 处罚日期
        #
        # Penalty_doc_num = '冀环罚' + re.findall('冀环罚(.*?)号', content)[0] + '号'  # 处罚文书号
        # Company_name = re.findall('号(.*?)：', content)[0]  # 单位名称
        # Offences = re.findall('环境违法行为：(.*?)以上事实', content)[0]  # 违法事由
        #
        # # 处罚依据
        # Punishment_basis = re.findall('(依据)(.*?)的规定', content)[0][1]
        # Punishment_basis = re.findall('《(.*?)》', Punishment_basis)
        # Punishment_basis = ["《" + i + "》" for i in Punishment_basis]
        # Punishment_basis = ','.join(Punishment_basis)
        #
        # Penalty_content = re.findall('下行政处罚：(.*?)收款银行', content)[0]  # 处罚内容
        # penalty_unit = '河北省生态环境厅'  # 处罚单位
        #
        # #处罚金额
        # if '罚款' in Penalty_content:
        #     Penalty_amount = re.findall('(罚款)(.*?)(元)', Penalty_content)[0][1]
        #     Penalty_amount = rmbtrans(Penalty_amount)
        # else:
        #     Penalty_amount = None
        #
        # item['Penalty_date'] = Penalty_date
        # item['Penalty_doc_num'] = Penalty_doc_num
        # item['penalty_unit'] = penalty_unit
        # item['Company_name'] = Company_name
        # item['Offences'] = Offences
        # item['Punishment_basis'] = Punishment_basis
        # item['Penalty_content'] = Penalty_content
        # item['Penalty_amount'] = Penalty_amount
        # item['pageurl'] = response.url
        # yield item


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
