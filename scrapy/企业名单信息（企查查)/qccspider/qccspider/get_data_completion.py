# -*- coding: utf-8 -*-
# @Date    : 2022-10-26 17:13
# @Author  : chenxuepeng
import time
import math
import json
import logging
import os
import re
import opencc
import requests
import xlrd
from lxml import etree
from decorator_penr import *
from qcc_hmac import *
from useragent import *
from qccspider.pymysql_connection import *
from redis_conn import *
from data_process import *
from qcc_outspider import outspider
from qccspider.config import *


class QccSpider():

    def __init__(self):
        self.i = 1
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.logger = self.log()
        self.qcc_item_dict = {
            '企业标签': 'label',
            'level': 'level',
            'type': 'type',
            '统一社会信用代码': 'credit_code',
            '企业名称': 'name',
            '公司名称': 'name',
            'search_name': 'search_name',
            '负责人': 'legal_representative',
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
        self.headers = {"User-Agent": self.ua}
        """股东信息-headers"""
        self.headers_data = {
            "content-type": "application/json",
            "cookie": self.open_cookie('cookie_data'),
            'user-agent': get_ua(),
        }

        self.redis_conn = redis_conn()


    def qccdata(self, id=None):
        if id:
            sql = 'select * from buy_business_qccdata where id=%s' % id
        else:
            sql = 'select id, pageurl, name from buy_business_qccdata where pageurl is not null'
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    """数据补全(股东信息，对外投资)"""
    def get_data_completion(self, sonname=None, sonid=None, types=None, level=None):
        redisConn = redis_conn()
        getData = self.qccdata()
        for item in getData:
            ids = item[0]
            pageurl = item[1]
            name = item[2]
            name = name if name else ''
            redisName = str(ids) + '_' + name
            investmentBool = redisConn.find_data(field='qcc_investment_new', value=redisName)
            shareholderBool = redisConn.find_data(field='qcc_shareholderinformation_new', value=redisName)
            print('当前:', pageurl)
            if not investmentBool:
                self.spider_investment(url=pageurl, ids=ids, redsi_name=redisName)
                time.sleep(5)
            else:
                print('对外投资已存在')

            if not shareholderBool:
                self.spider_shareholder(url=pageurl, ids=ids, redsi_name=redisName)
                time.sleep(5)
            else:
                print('股东信息已存在')



    @retry(exceptions=True, max_retries=10)
    def spider_shareholder(self, url, ids, redsi_name):
        qcc_conn = pymysql_connection()
        keyid = re.findall('firm/(.*?)\.html', url)
        keyid = keyid[0] if keyid else keyid
        """股东信息"""
        shareholder = self.getshareholder(
            url='https://www.qcc.com/api/datalist/partner',
            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi&type=IpoPartners' % keyid,
            keyid=keyid,
            new=True,
            type=0
        )
        if not shareholder:
            shareholder = self.getshareholder(
                url='https://www.qcc.com/api/datalist/partner',
                data='isSortAsc=&keyNo=%s&pageIndex=1&pageSize=50&sortField=' % keyid,
                keyid=keyid,
                new=True,
                type=2
            )

        if shareholder is None:
            print('股东信息不存在')
        else:
            qcc_conn.insert_shareholderinformation_new(item=shareholder, insert_id=ids, redsi_name=redsi_name)


    @retry(exceptions=True, max_retries=10)
    def spider_investment(self, url, ids, redsi_name):
        qcc_conn = pymysql_connection()
        keyid = re.findall('firm/(.*?)\.html', url)
        keyid = keyid[0] if keyid else keyid
        investment = self.getoutbound(
            url='https://www.qcc.com/api/datalist/touzilist',
            data='keyNo=%s&pageIndex=1' % keyid,
            keyid=keyid,
            pageindex=1,
            new=True,
        )
        if investment:
            qcc_conn.insert_qcc_investment_new(item=investment, insert_id=ids, redsi_name=redsi_name)
        else:
            print('对外投资为空')

        # qcc_conn.qcc_insert(key=sql_key, value=sql_value, shareholder=shareholder,
        #                     investment=outbound, type=self.type, uuid=search_key)
        # qcc_conn.close()

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

    @retry(max_retries=10)
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
        response = requests.get(url=url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'}, timeout=1)
        Set_Cookie = response.headers.get('Set-Cookie')
        get_keys = re.findall('(acw_tc|QCCSESSID)(.*?);', Set_Cookie)
        cookies = [''.join(i) for i in get_keys]
        cookie = '; '.join(cookies)
        print(f'获取cookie成功{response.history}:', cookie)
        if response.history:
            raise ValueError('获取cookie失败')
        else:
            return cookie

    def save_cookie(self):
        with open('./config.json', 'r')as f:
            r = json.loads(f.read())
        r.update({'cookie': self.get_cookie()})
        with open('./config.json', 'w')as f:
            f.write(json.dumps(r, ensure_ascii=False))

    def open_cookie(self, type='cookie'):
        if self.i % 50 == 1:
            self.save_cookie()
        with open('./config.json', 'r')as f:
            r = json.loads(f.read())
        self.i += 1
        return r.get(type)

    def get_hmac(self, type=0, keyno=None, tid='c7471078d8d101a605235f57d5887e4d', new=None, pageindex=None):
        """
        :param keyno: 公司唯一标识：b8d99d133f16f34f30f7224145d8ec6f(https://www.qcc.com/firm/b8d99d133f16f34f30f7224145d8ec6f.html)
        :param tid: window.tid
        :return: 0: 股权穿透图子集, 1: 股权穿透图父集
        """
        return gethmac(keyno=keyno, tid=tid, new=new, qtypy=type, pageindex=pageindex)

    @retry(delay=2, exceptions=True, max_retries=5)
    def getshareholder(self, url, data, keyid, new, type):
        getcookie = self.get_hmac(type=type, keyno=keyid, new=new)
        header = copy.deepcopy(self.headers_data)
        header.update(getcookie)
        item_list = []
        response = requests.get(url=url, headers=header, params=data)
        code = response.status_code
        try:
            datas = response.json().get('data')
            if datas:
                print(f'正在获取股东信息:{code}, 数量:', response.json().get('pageInfo').get('total'))
                for qdata in datas:
                    item_dict = {}
                    StockName = qdata.get('StockName', '-')  # 股东及出资信息
                    ShareType = qdata.get('ShareType', '-')  # 股份类型
                    StockPercent = qdata.get('StockPercent', '-')  # 持股比例
                    ShouldCapi = qdata.get('TotalShouldAmount', '-')  # 持股数(股)
                    RegistCapi = qdata.get('RegistCapi', '-')  # 认缴出资额(万元)
                    ShoudDate = qdata.get('ShoudDate', '-')  # 认缴出资日期
                    ShoudDate = ShoudDate if ShoudDate else '-'
                    ShoudDate = ShoudDate.split(',')[-1] if ',' in ShoudDate else ShoudDate
                    FinalBenefitPercent = qdata.get('FinalBenefitPercent', '-')  # 最终受益股份
                    InDate = qdata.get('InDate', '-')  # 首次持股日期
                    Name = qdata.get('Product')  # 关联产品/机构
                    ProductName = Name.get('Name', '-') if Name else '-'  # 关联产品/机构
                    item_dict['StockName'] = StockName
                    item_dict['ShareType'] = ShareType
                    item_dict['StockPercent'] = StockPercent
                    item_dict['ShouldCapi'] = ShouldCapi
                    item_dict['RegistCapi'] = RegistCapi
                    item_dict['ShoudDate'] = ShoudDate
                    item_dict['FinalBenefitPercent'] = FinalBenefitPercent
                    item_dict['InDate'] = InDate
                    item_dict['ProductName'] = ProductName
                    item_list.append(item_dict)
                return item_list

        except Exception as e:
            if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                print('股东信息获取失败:', code, e)
                input("\033[1;32m请验证账号\033[0m")
                raise ValueError("请验证账号")

    @retry(delay=2, exceptions=True, max_retries=5)
    def getoutbound(self, url=None, data=None, keyid=None, new=None, pageindex=None):
        getcookie = self.get_hmac(type=1, keyno=keyid, pageindex=pageindex)
        header = copy.deepcopy(self.headers_data)
        header.update(getcookie)
        item_list = []
        response = requests.get(url=url, headers=header, params=data)
        code = response.status_code
        try:
            datas = response.json().get('data')
            if datas:
                page = math.ceil(response.json().get('pageInfo').get('total') / 10)
                page = int(page)
                print(f'正在获取对外投资信息:{code}, 页数:', page)
                for qdata in datas:
                    item_dict = {}
                    Name = qdata.get('Name', '-')  # 被投资企业名称
                    Status = qdata.get('Status', '-')  # 状态
                    FundedRatio = qdata.get('FundedRatio', '-')  # 持股比例
                    ShouldCapi = qdata.get('ShouldCapi', '-')  # 认缴出资额/持股数
                    ShouldDate = qdata.get('ShouldDate', '-')  # 认缴出资日期
                    ProvinceName = qdata.get('ProvinceName', '-')  # 所属省份
                    IndustryItem = qdata.get('IndustryItem')  # 所属行业
                    Industry = IndustryItem.get('Industry') if IndustryItem else '-'  # 所属行业
                    Product = qdata.get('Product')  # 关联产品/机构
                    ProductName = Product.get('Name') if Product else '-'  # 关联产品/机构
                    item_dict['Status'] = Status
                    item_dict['FundedRatio'] = FundedRatio
                    item_dict['ShouldCapi'] = ShouldCapi
                    item_dict['ShouldDate'] = ShouldDate
                    item_dict['ProvinceName'] = ProvinceName
                    item_dict['Industry'] = Industry
                    item_dict['ProductName'] = ProductName
                    item_dict['StockName'] = Name
                    item_list.append(item_dict)

                if page > 1:
                    for i in range(2, page + 1):
                        time.sleep(2)

                        print(f'正在抓取第{i}页.')
                        outbound = self.getoutbound2(
                            url='https://www.qcc.com/api/datalist/touzilist',
                            data=f'keyNo=%s&pageIndex={i}' % keyid,
                            keyid=keyid,
                            pageindex=i,
                            new=True,
                        )
                        for k in outbound:
                            item_list.append(k)
                        time.sleep(1)

                return item_list

        except Exception as e:
            if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                print('对外投资失败:', code, e)
                input("\033[1;33m请验证账号\033[0m")
                raise ValueError("请验证账号")

    @retry(delay=2, exceptions=True, max_retries=5)
    def getoutbound2(self, url=None, data=None, keyid=None, new=None, pageindex=None):
        getcookie = self.get_hmac(type=1, keyno=keyid, pageindex=pageindex)
        header = copy.deepcopy(self.headers_data)
        header.update(getcookie)
        item_list = []
        response = requests.get(url=url, headers=header, params=data)
        response.encoding = 'utf-8'
        code = response.status_code
        try:
            datas = response.json().get('data')
            if datas:
                for qdata in datas:
                    item_dict = {}
                    Name = qdata.get('Name')  # 被投资企业名称
                    Status = qdata.get('Status')  # 状态
                    FundedRatio = qdata.get('FundedRatio')  # 持股比例
                    ShouldCapi = qdata.get('ShouldCapi')  # 认缴出资额/持股数
                    ShouldDate = qdata.get('ShouldDate')  # 认缴出资日期
                    ProvinceName = qdata.get('ProvinceName')  # 所属省份
                    IndustryItem = qdata.get('IndustryItem')  # 所属行业
                    Industry = IndustryItem.get('Industry') if IndustryItem else '-'  # 所属行业
                    Product = qdata.get('Product')  # 关联产品/机构
                    ProductName = Product.get('Name') if Product else '-'  # 关联产品/机构
                    item_dict['Status'] = Status
                    item_dict['FundedRatio'] = FundedRatio
                    item_dict['ShouldCapi'] = ShouldCapi
                    item_dict['ShouldDate'] = ShouldDate
                    item_dict['ProvinceName'] = ProvinceName
                    item_dict['Industry'] = Industry
                    item_dict['ProductName'] = ProductName
                    item_dict['StockName'] = Name
                    item_list.append(item_dict)
                return item_list
        except Exception as e:
            if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                print('对外投资失败:', code, e)
                input("\033[1;33m请验证账号\033[0m")
                raise ValueError("请验证账号")



if __name__ == '__main__':
    x = QccSpider().get_data_completion()
