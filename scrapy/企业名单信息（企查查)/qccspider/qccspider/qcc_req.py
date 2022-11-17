# -*- coding: utf-8 -*-
# @Date    : 2022-10-26 17:13
# @Author  : chenxuepeng
import logging, json
import xlrd
import os, sys
import re
import requests
from lxml import etree

from pymysql_connection import *
from useragent import *
from decorator_penr import *
from qcc_hmac import *


class QccSpider():

    def __init__(self):
        self.logger = self.log()
        self.qcc_item_dict = {
            '企业标签': 'label',
            '统一社会信用代码': 'credit_code',
            '企业名称': 'name',
            '法定代表人': 'legal_representative',
            '登记状态': 'registration_status',
            '状态': 'status',
            '成立日期': 'incorporation_date',
            '注册资本': 'registered_capital',
            '实缴资本': 'paid_capital',
            '组织机构代码': 'organization_code',
            '工商注册号': 'business_code',
            '纳税人识别号': 'taxpayer_code',
            '企业类型': 'enterprise_type',
            '纳税人资质': 'taxpayer_qualification',
            '人员规模': 'personnel_size',
            '参保人数': 'insured_num',
            '核准日期': 'approval_date',
            '所属地区': 'area',
            '登记机关': 'organ',
            '进出口企业代码': 'io_code',
            '所属行业': 'industry',
            '英文名': 'english_name',
            '注册地址': 'address',
            '经营范围': 'business_scope',
            '最新年报地址': 'report_latest',
            '营业期限': 'business_term',
            '网站链接': 'pageurl',
        }
        self.ua = get_ua()
        """工商信息-headers"""
        self.headers = {
            "Host": "www.qcc.com",
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "https://www.qcc.com/web/search?key=",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cookie": self.open_cookie()
        }

        """股权穿透图-headers"""
        self.headers_data = {
            "content-type": "application/json",
            "cookie": self.open_cookie('cookie_data'),
            'user-agent': get_ua(),
        }

    @retry(delay=5, exceptions=True, max_retries=5)
    def start_request(self, search_key):
        '''数据查询去重-去除重复采购单位'''
        headers = self.headers
        condition = True  # False：在企查查中匹配到数据; Ture:在企查查未匹配到数据
        search_id = 1
        # search_key = '中国核工业集团有限公司'
        search_key = search_key
        print('当前: ', search_key)
        search_url = f'https://www.qcc.com/web/search?key={search_key}'
        response = requests.get(search_url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'})
        response.encoding = 'utf-8'
        '''状态码判断'''
        if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
            error_msg = re.findall('(<title>.*?</title>)', response.text)[0]
            loginfo = f'Status: False, Status_code: {response.status_code}, url: {search_url}, msg: {error_msg}'
            self.logger.info(loginfo)
            raise ValueError('异常请求, 请求失败===>>>', search_url)

        else:
            print(200, search_id, search_url)
            tree = etree.HTML(response.text)
            maininfo = tree.xpath("//div[@class='maininfo']")
            for item in maininfo:
                if condition is True:
                    company_name = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']//text()")
                    company_name = ''.join(company_name)
                    if company_name == search_key:
                        curl = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']/@href")[0]
                        tags = item.xpath(".//span[@class='search-tags']/span[@class='m-r-sm']/span/text()")
                        tags = [i.strip() for i in tags]
                        tags = ','.join(tags)
                        '''
                        解析字段
                        '''
                        time.sleep(2)
                        self.cparse(curl, tags, headers)
                        condition = False
                        print('===========')
                else:
                    break

            '''企查查未找到'''
            if condition is True:
                print('Not Found')
                self.logger.info(f'Not Found:名称 {search_key}; id: {search_id}; url: {search_url}')

    @retry(delay=2, exceptions=True, max_retries=5)
    def cparse(self, url, tags, headers):
        qcc_conn = pymysql_connection()
        keyid = re.findall('firm/(.*?)\.html', url)
        keyid = keyid[0] if keyid else keyid
        item = {}
        qcc_value_list = []
        qcc_key_list = []

        response = requests.get(url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'})
        if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
            raise ValueError('异常访问,访问失败===>>>', url)
        response.encoding = 'utf-8'
        resp = etree.HTML(response.text)
        obj = resp.xpath("//div[@class='cominfo-normal']/table/tr")
        for i in obj:
            value_list = []
            qcc_key = i.xpath(".//td[@class='tb']")
            qcc_key = [i.xpath('.//text()')[0].strip() for i in qcc_key]
            qcc_value = i.xpath("./td[2]|./td[4]|./td[6]")

            for v in qcc_value:
                v_text = v.xpath(
                    ".//a[@class='text-dk copy-value']/text()|.//span[@class='cont']/span/span/a/text()|.//span[@class='copy-value']/text()")
                if v_text:
                    value_list.append(v_text[0].strip())
                else:
                    v_text = v.xpath('.//text()')
                    v_text = ''.join(v_text).replace('\n', '').strip()
                    v_text = ''.join(v_text.split())
                    value_list.append(v_text)

            len_k = len(qcc_key)
            len_v = len(value_list)

            if len_k != len_v:
                raise ValueError('字段长度不匹配, 请重新检测网站===>>>', url)
            else:
                for i in range(len_k):
                    item[qcc_key[i]] = value_list[i]

        item['参保人数'] = item.get('参保人数').replace('趋势图', '')
        item['网站链接'] = url
        item['企业标签'] = tags

        sql_key_list = []
        sql_value_list = []
        for k,v in item.items():
            sql_key_list.append(self.qcc_item_dict.get(k))
            sql_value_list.append(v)

        sql_key = ','.join(sql_key_list)
        sql_value_list = ['"' + i + '"' for i in sql_value_list]
        sql_value = ','.join(sql_value_list)

        """数据入库"""
        qcc_conn.qcc_insert(sql_key, sql_value)


        """股权穿透图"""
        getcookie = self.get_hmac(keyno=keyid)
        sonheader = copy.deepcopy(self.headers_data)
        sonheader.update(getcookie[0])
        sondata = '{"keyNo": "%s"}' % keyid
        sonurl = 'https://www.qcc.com/api/charts/getEquityInvestment'
        sonresult = self.getEquityInvestment(url=sonurl, headers=sonheader, data=sondata)
        print('获取到股权穿透图-子级:', sonresult)

        fatherheader = copy.deepcopy(self.headers_data)
        fatherheader.update(getcookie[1])
        fatherdata = '{"keyNo": "%s","level":1}' % keyid
        fatherurl = 'https://www.qcc.com/api/charts/getOwnershipStructureMix'
        fatherresult = self.getOwnershipStructureMix(url=fatherurl, headers=fatherheader, data=fatherdata)
        print('获取到股权穿透图-父级:', fatherresult)
        time.sleep(5)

    def log(self):
        os.makedirs('./loging', exist_ok=True)
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("./loging/log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def get_cookie(self):
        url = 'https://www.qcc.com/ '
        headers = {
            "Host": "www.qcc.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        response = requests.get(url=url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'})
        Set_Cookie = response.headers.get('Set-Cookie')
        get_keys = re.findall('(acw_tc|QCCSESSID)(.*?);', Set_Cookie)
        cookies = [''.join(i) for i in get_keys]
        cookie = '; '.join(cookies)
        print(cookie)
        return cookie

    def open_cookie(self, type='cookie'):
        with open('./config.json', 'r')as f:
            r = json.loads(f.read())
        return r.get(type)

    def get_hmac(self, keyno=None, tid='a026f74acbc7e5aab3c6d6b42e3547cf'):
        """
        :param keyno: 公司唯一标识：b8d99d133f16f34f30f7224145d8ec6f(https://www.qcc.com/firm/b8d99d133f16f34f30f7224145d8ec6f.html)
        :param tid: window.tid
        :return: 0: 股权穿透图子集, 1: 股权穿透图父集
        """
        k1 = getequityinvestment(keyno, tid)
        k2 = getownershipstructuremix(keyno, tid)
        return k1, k2

    @retry(delay=2, exceptions=True, max_retries=5)
    def getEquityInvestment(self, url, headers, data):
        print('正在获取股权穿透图-子集')
        item_list = []
        response = requests.post(url=url, headers=headers, data=data)
        Result = response.json().get('Result')
        if Result:
            EquityShareDetail = Result.get('EquityShareDetail')
            for k in EquityShareDetail:
                item = {}
                name = k.get('Name')
                level = k.get('Level')
                percent = k.get('Percent')
                percenttotal = k.get('PercentTotal')
                registcapi = k.get('RegistCapi')
                shortstatus = k.get('ShortStatus')
                shouldcapi = k.get('ShouldCapi')

                item['name'] = name
                item['level'] = level
                item['percent'] = percent
                item['percenttotal'] = percenttotal
                item['registcapi'] = registcapi
                item['shortstatus'] = shortstatus
                item['shouldcapi'] = shouldcapi
                item['org'] = 0
                item_list.append(item)
            return item_list
        else:
            raise ValueError('数据获取失败')

    @retry(delay=2, exceptions=True, max_retries=5)
    def getOwnershipStructureMix(self, url, headers, data):
        print('正在获取股权穿透图-父集')
        item_list = []
        response = requests.post(url=url, headers=headers, data=data)
        Result = response.json().get('structure')
        if Result:
            EquityShareDetail = Result.get('EquityShareDetail')
            for k in EquityShareDetail:
                item = {}
                name = k.get('Name')
                level = k.get('Level')
                percent = k.get('Percent')
                percenttotal = k.get('PercentTotal')
                registcapi = k.get('RegistCapi')
                shortstatus = k.get('ShortStatus')
                shouldcapi = k.get('ShouldCapi')
                stocktype = k.get('StockType')

                item['name'] = name
                item['level'] = level
                item['percent'] = percent
                item['percenttotal'] = percenttotal
                item['registcapi'] = registcapi
                item['shortstatus'] = shortstatus
                item['shouldcapi'] = shouldcapi
                item['stocktype'] = stocktype
                item['org'] = 2
                item_list.append(item)
            return item_list
        else:
            raise ValueError('数据获取失败')

class QccXls:
    def __init__(self):
        pass

    def get_xls_data(self):
        # 打开excel
        wb_list = []
        wb = xlrd.open_workbook('央企+双百企业名单合集-1114.xls')
        # 按工作簿定位工作表
        sh = wb.sheet_by_name('企业名单合集')
        for i in range(sh.nrows):
            data = sh.row_values(i)[3] if re.findall('\d', str(sh.row_values(i)[2])) else sh.row_values(i)[2]
            wb_list.append(data)
        return wb_list[1:]



if __name__ == '__main__':
    q = QccSpider()
    x = QccXls().get_xls_data()
    for name in x:
        q.start_request(name)
