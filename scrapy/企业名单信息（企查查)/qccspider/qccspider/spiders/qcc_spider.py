# -*- coding: utf-8 -*-
# @Date    : 2022-11-15 15:57
# @Author  : chenxuepeng
import scrapy, requests, re
from ..useragent import *
from ..data_process import *


class QccSpider(scrapy.Spider):
    name = 'spider'
    search_key = '航天科工空间工程发展有限公司'
    headers = {
        "Host": "www.qcc.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "https://www.qcc.com/web/search?key=",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def start_requests(self):
        search_url = f'https://www.qcc.com/web/search?key={self.search_key}'
        yield scrapy.Request(url=search_url, headers=self.headers, callback=self.parse,
                             meta={'dont_redirect': True, "handle_httpstatus_list": [302]})

    def parse(self, response, **kwargs):
        condition = True
        maininfo = response.xpath("//div[@class='maininfo']")
        for item in maininfo:
            if condition is True:
                company_name = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']//text()").getall()
                company_name = ''.join(company_name)
                if company_name == self.search_key:
                    condition = False
                    curl = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']/@href").getall()[0]
                    tags = item.xpath(".//span[@class='search-tags']/span[@class='m-r-sm']/span/text()").getall()
                    tags = [i.strip() for i in tags]
                    tags = ','.join(tags)
                    yield scrapy.Request(url=curl, headers=self.headers, callback=self.cparse, meta=
                    {
                        'dont_redirect': True, "handle_httpstatus_list": [302], 'tags': tags,
                    })
                    '''
                    解析字段
                    '''
                else:
                    break

        if condition is True:
            # self.logger.info(f'Not Found:名称 {self.search_key};  url: {response.url}')
            print('Not Found:', response.url)

    def cparse(self, response):
        item = {}
        label = response.meta['tags']  # 企业标签
        obj = response.xpath("//div[@class='cominfo-normal']/table/tr")
        for i in obj:
            qcc_key = i.xpath("./td[@class='tb']")
            qcc_value = i.xpath("./td[2]|./td[4]|./td[6]")
            qcc_key = [i.xpath('.//text()').getall() for i in qcc_key]

            qcc_value_list = []
            for v in qcc_value:
                v_text = v.xpath(".//a[@class='text-dk copy-value']/text()|.//span[@class='cont']/span/span/a/text()|.//span[@class='copy-value']/text()")
                if v_text:
                    qcc_value_list.append(v_text.getall()[0])
                else:
                    v_text = v.xpath('.//text()').getall()
                    qcc_value_list.append(v_text)

            print(qcc_key, qcc_value_list)

        # credit_code = obj.xpath("//table[@class='ntable']/tr[1]/td[2]//span[@class='copy-value']")  # 统一社会信用代码
        # name = obj.xpath("//table[@class='ntable']/tr[1]/td[4]/div/span[@class='copy-value']")  # 企业名称
        # legal_representative = obj.xpath("//table[@class='ntable']/tr[2]/td[@class='base-opertd']//span[@class='cont']/span/span/a")  # 法定代表人
        # status = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[2]/td[4]")  # 登记状态
        # incorporation_date = obj.xpath("//table[@class='ntable']/tr[2]/td[6]/div/span[@class='copy-value']")  # 成立日期
        # paid_capital = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[3]/td[4]")  # 实缴资本
        # organization_code = obj.xpath("//table[@class='ntable']/tr[4]/td[2]/div/span[@class='copy-value']")  # 组织机构代码
        # business_code = obj.xpath("//table[@class='ntable']/tr[4]/td[4]/div/span[@class='copy-value']")  # 工商注册号
        # taxpayer_code = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[5]/td[2]")  # 企业类型
        # taxpayer_qualification = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[5]/td[6]")  # 纳税人资质
        # personnel_size = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[6]/td[2]")  # 人员规模
        # insured_num = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[6]/td[4]")  # 参保人数
        # approval_date = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[6]/td[6]/div/span[@class='copy-value']")  # 核准日期
        # area = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[7]/td[2]")  # 所属地区
        # organ = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[7]/td[4]")  # 登记机关
        # io_code = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[7]/td[6]")  # 进出口企业代码
        # industry = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[8]/td[2]")  # 所属行业
        # english_name = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[8]/td[4]/div//span[@class='copy-value']")  # 英文名
        # address = obj.xpath("//div[@class='cominfo-normal']/table[@class='ntable']/tr[9]/td[2]/div/span/a[@class='text-dk copy-value']")  # 注册地址
        # business_scope = obj.xpath("")  # 经营范围
