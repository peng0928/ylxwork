# -*- coding: utf-8 -*-
# @Date    : 2022-10-26 17:13
# @Author  : chenxuepeng
import copy
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

    def __init__(self, type, level):
        self.i = 1
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
        self.type = type
        self.level = level

    @retry(exceptions=True, max_retries=10)
    def start_request(self, search_key, id=None, code=None, cspider=False):
        self.notfound = {}
        self.nottag = []
        '''数据查询去重-去除重复采购单位'''
        headers = {}
        headers.update({"User-Agent": get_ua()})
        headers.update({"cookie": self.open_cookie()})
        condition = True  # False：在企查查中匹配到数据; Ture:在企查查未匹配到数据
        search_id = 1
        # search_key = 'TCL科技集团(天津)有限公司'
        search_key = search_key.replace(' ', '')

        print('当前: ', search_key, id)
        search_redis = self.redis_conn.find_data(field='qcc_qccdata', value=search_key)
        # search_redis = False
        if search_redis:
            print('已存在：', search_key)
        else:
            search_url = f'https://www.qcc.com/web/search?key={search_key}'
            response = requests.get(search_url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'})
            response.encoding = 'utf-8'
            '''状态码判断'''
            if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                error_msg = re.findall('(<title>.*?</title>)', response.text)[0]
                # loginfo = f'Status: False, Status_code: {response.status_code}, url: {search_url}, msg: {error_msg}'
                # self.logger.info(loginfo)
                raise ValueError('异常请求, 请求失败===>>>', search_url)

            else:
                print(200, search_id, search_url)
                tree = etree.HTML(response.text)
                maininfo = tree.xpath("//div[@class='maininfo']")
                numi = 0
                for item in maininfo:
                    if condition is True:
                        company_names = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']//text()")
                        company_names = ''.join(company_names)
                        # cc = opencc.OpenCC('t2s')
                        # company_name = cc.convert(company_names.replace('（', '(').replace('）', ')')) # 企业名称：繁体转简体
                        company_name = (company_names.replace('（', '(').replace('）', ')'))
                        curl = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']/@href")[0]
                        tags = item.xpath(".//span[@class='search-tags']/span[@class='m-r-sm']/span/text()")
                        tags = tags if tags else '-'
                        tags = [i.strip() for i in tags]
                        tags = ','.join(tags)
                        numi += 1
                        print(numi, company_name, search_key)
                        d = {company_name: curl}
                        self.notfound[numi] = d
                        self.nottag.append(tags)
                        if company_name == search_key:
                            '''
                            解析字段
                            '''
                            time.sleep(1)
                            if cspider:
                                self.cspider(curl, tags, search_key, id)
                                condition = False
                            else:
                                self.cparse(curl, tags, search_key, id=id, code=code)
                                condition = False
                            print('===========')
                    else:
                        break

                '''企查查未找到'''
                if condition is True:
                    print(self.notfound)
                    sinput = 'q'
                    if sinput != 'q':
                        sname = self.notfound.get(int(sinput))
                        for k, v in sname.items():
                            self.cparse(v, self.nottag[int(sinput)], search_key)
                    else:
                        self.logger.info(f'Not Found:名称 {search_key}')

    @retry(exceptions=True, max_retries=10)
    def cparse(self, url, tags, search_key, id=None, code=None):
        headers = {}
        headers.update({"User-Agent": get_ua()})
        headers.update({"cookie": self.open_cookie()})

        qcc_conn = pymysql_connection()
        keyid = re.findall('firm/(.*?)\.html', url)
        keyid = keyid[0] if keyid else keyid
        item = {}
        response = requests.get(url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'}, timeout=3)
        if '公司不存在' in response.text:
            print(f'{search_key}公司不存在:{url}')
        elif str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
            raise ValueError('异常访问,访问失败===>>>', url)
        else:
            response.encoding = 'utf-8'
            resp = etree.HTML(response.text)
            obj = resp.xpath(
                "//div[@class='cominfo-normal']/table/tr|//section[@id='hkregisterinfo']/table[@class='ntable']/tr")
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
                        v_text = ''.join(v_text).replace('\n', '').strip() if v_text else v_text
                        v_text = ''.join(v_text.split())
                        value_list.append(v_text)

                len_k = len(qcc_key)
                len_v = len(value_list)

                if len_k != len_v:
                    raise ValueError('字段长度不匹配, 请重新检测网站===>>>', url)
                else:
                    for i in range(len_k):
                        item[qcc_key[i]] = value_list[i]

            item['参保人数'] = item.get('参保人数').replace('趋势图', '') if item.get('参保人数') else item.get('参保人数')
            item['网站链接'] = url
            item['type'] = self.type
            item['企业标签'] = tags if tags else 'null'

            sql_key_list = []
            sql_value_list = []
            item['level'] = self.level

            for k, v in item.items():
                ak = self.qcc_item_dict.get(k)
                if ak and v:
                    sql_key_list.append(ak)
                    sql_value_list.append(v)

            sql_key = ','.join(sql_key_list)
            sql_value_list = ['"' + str(i) + '"' for i in sql_value_list]
            sql_value = ','.join(sql_value_list)
            ilist = []
            for i in range(len(sql_key_list)):
                ilist.append(sql_key_list[i] + '=' + sql_value_list[i])
            ilist = ','.join(ilist)
            """工商数据"""
            print('获取到工商数据:', keyid)
            print(ilist, id, code)

            """股东信息"""
            shareholder_x = resp.xpath(
                "//section[@id='hkpartner']/div[@class='tcaption']/h3[@class='title']//text()|//section[@id='partner']//h3[@class='title']//text()")
            shareholder_x = ''.join(shareholder_x)
            shareholder_x = re.sub('\d', '', shareholder_x)
            if shareholder_x == '股东信息':
                shareholder_new = resp.xpath(
                    "//section[@id='partner']//span[@class='tab-item'][1]//span[@class='item-title']/text()")
                if shareholder_new:
                    if shareholder_new[0] == '最新公示':
                        shareholder = self.getshareholder(
                            url='https://www.qcc.com/api/datalist/partner',
                            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi&type=IpoPartners' % keyid,
                            keyid=keyid,
                            new=True,
                        )
                    else:
                        shareholder = self.getshareholder(
                            url='https://www.qcc.com/api/datalist/partner',
                            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi' % keyid,
                            keyid=keyid,
                            new=False,
                        )
                else:
                    normal = resp.xpath("//th[@class='has-sort-th']//text()")
                    normal = ''.join(normal)
                    if '持股比例' in normal:
                        shareholder = self.getshareholder(
                            url='https://www.qcc.com/api/datalist/partner',
                            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi' % keyid,
                            keyid=keyid,
                            new=False,
                        )
                    else:
                        normal_list = []
                        normal_table_list = []
                        msg_dict = {
                            '股东(发起人)': 'StockName',
                            '持股比例': 'StockPercent',
                            '持股数(股)': 'ShouldCapi',
                            '公示日期': 'Publicitydate',
                        }
                        normal_xpath = "//section[@id='hkpartner']//table[@class='ntable']/tr[position()>1]"
                        normal_table = resp.xpath(
                            "//section[@id='hkpartner']//table[@class='ntable']/tr[position()=1]/th")
                        for normal_item in normal_table:
                            normal_table_list.append(''.join(normal_item.xpath('./text()')).strip())
                        print(normal_table_list)
                        normal_x = resp.xpath(normal_xpath)
                        for item2 in normal_x:  # 循环一次为表格一行
                            normal_dict = {}
                            normal_x2 = item2.xpath("./td")  # 获取表单td长度
                            for len_n in range(len(normal_x2)):  # 循环每个td
                                normal_key = msg_dict.get(normal_table_list[len_n])
                                if normal_key:
                                    normal_text = normal_x2[len_n].xpath(".//text()")  # 数据
                                    normal_dict[normal_key] = ''.join(normal_text).strip()
                                else:
                                    if normal_table_list[len_n] == '序号':
                                        pass
                                    else:
                                        input(f'字段不存在请检查："{normal_table_list[len_n]}"')
                            normal_list.append(normal_dict)
                        shareholder = normal_list
            else:
                shareholder = None
                print('股东信息不存在...', shareholder_x)

            """对外投资outbound"""
            outbound_x = resp.xpath("//section[@id='touzilist']//h3[@class='title']//text()")
            outbound_x = ''.join(outbound_x)
            outbound_x = re.sub('\d', '', outbound_x)
            if outbound_x == '对外投资':
                outbound = self.getoutbound(
                    url='https://www.qcc.com/api/datalist/touzilist',
                    data='keyNo=%s&pageIndex=1' % keyid,
                    keyid=keyid,
                    pageindex=1,
                    new=True,
                )
            else:
                outbound = None
                print('对外投资不存在...')

            if shareholder is None and outbound is None:
                # if outbound is None:
                input(f'对外投资， 股东信息都为空，请确定!{url}')
                # print(f'对外投资， 股东信息都为空，请确定!', url)
                # outbound = ''
            qcc_conn.qcc_insert(key=sql_key, value=sql_value, shareholder=shareholder,
                                investment=outbound, Type=None, searchName=None)
            qcc_conn.close()

    @retry(exceptions=True, max_retries=10)
    def cspider(self, url, tags, search_key, ids):
        headers = {}
        headers.update({"User-Agent": get_ua()})
        headers.update({"cookie": self.open_cookie()})

        qcc_conn = pymysql_connection()
        keyid = re.findall('firm/(.*?)\.html', url)
        keyid = keyid[0] if keyid else keyid
        item = {}
        response = requests.get(url, headers=headers, proxies={'https': 'tps163.kdlapi.com:15818'}, timeout=3)
        if '公司不存在' in response.text:
            print(f'{search_key}公司不存在:{url}')
        elif str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
            raise ValueError('异常访问,访问失败===>>>', url)
        else:
            response.encoding = 'utf-8'
            resp = etree.HTML(response.text)
            obj = resp.xpath(
                "//div[@class='cominfo-normal']/table/tr|//section[@id='hkregisterinfo']/table[@class='ntable']/tr")
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
                        v_text = ''.join(v_text).replace('\n', '').strip() if v_text else v_text
                        v_text = ''.join(v_text.split())
                        value_list.append(v_text)

                len_k = len(qcc_key)
                len_v = len(value_list)

                if len_k != len_v:
                    raise ValueError('字段长度不匹配, 请重新检测网站===>>>', url)
                else:
                    for i in range(len_k):
                        item[qcc_key[i]] = value_list[i]

            item['参保人数'] = item.get('参保人数').replace('趋势图', '') if item.get('参保人数') else item.get('参保人数')
            item['网站链接'] = url
            item['type'] = self.type
            item['企业标签'] = tags if tags else 'null'

            sql_key_list = []
            sql_value_list = []
            item['level'] = self.level

            for k, v in item.items():
                ak = self.qcc_item_dict.get(k)
                if ak and v:
                    sql_key_list.append(ak)
                    sql_value_list.append(v.replace('"', '“').replace(',', '，'))

            sql_key = ','.join(sql_key_list)
            sql_value_list = ['"' + str(i) + '"' for i in sql_value_list]
            sql_value = ','.join(sql_value_list)
            ilist = []
            for i in range(len(sql_key_list)):
                ilist.append(sql_key_list[i] + '=' + sql_value_list[i])
            ilist = ','.join(ilist)

            """工商数据"""
            print('获取到工商数据:', keyid)

            """股东信息"""
            shareholder_x = resp.xpath(shareholder_xpath)
            shareholder_x = ''.join(shareholder_x)
            shareholder_x = re.sub('\d', '', shareholder_x)
            if shareholder_x == '股东信息':
                shareholder_new = resp.xpath(
                    "//section[@id='partner']//span[@class='tab-item'][1]//span[@class='item-title']/text()")
                if shareholder_new:
                    if shareholder_new[0] == '最新公示':
                        shareholder = self.getshareholder(
                            url='https://www.qcc.com/api/datalist/partner',
                            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi&type=IpoPartners' % keyid,
                            keyid=keyid,
                            new=True,
                        )
                    else:
                        shareholder = self.getshareholder(
                            url='https://www.qcc.com/api/datalist/partner',
                            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi' % keyid,
                            keyid=keyid,
                            new=False,
                        )
                else:
                    normal = resp.xpath("//th[@class='has-sort-th']//text()")
                    normal = ''.join(normal)
                    if '持股比例' in normal:
                        shareholder = self.getshareholder(
                            url='https://www.qcc.com/api/datalist/partner',
                            data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi' % keyid,
                            keyid=keyid,
                            new=False,
                        )
                    else:
                        normal_list = []
                        normal_table_list = []
                        msg_dict = {
                            '股东(发起人)': 'StockName',
                            '持股比例': 'StockPercent',
                            '持股数(股)': 'ShouldCapi',
                            '公示日期': 'Publicitydate',
                        }
                        normal_xpath = "//section[@id='hkpartner']//table[@class='ntable']/tr[position()>1]"
                        normal_table = resp.xpath(
                            "//section[@id='hkpartner']//table[@class='ntable']/tr[position()=1]/th")
                        for normal_item in normal_table:
                            normal_table_list.append(''.join(normal_item.xpath('./text()')).strip())
                        print(normal_table_list)
                        normal_x = resp.xpath(normal_xpath)
                        for item2 in normal_x:  # 循环一次为表格一行
                            normal_dict = {}
                            normal_x2 = item2.xpath("./td")  # 获取表单td长度
                            for len_n in range(len(normal_x2)):  # 循环每个td
                                normal_key = msg_dict.get(normal_table_list[len_n])
                                if normal_key:
                                    normal_text = normal_x2[len_n].xpath(".//text()")  # 数据
                                    normal_dict[normal_key] = ''.join(normal_text).strip()
                                else:
                                    if normal_table_list[len_n] == '序号':
                                        pass
                                    else:
                                        input(f'字段不存在请检查："{normal_table_list[len_n]}"')
                            normal_list.append(normal_dict)
                        shareholder = normal_list
            else:
                shareholder = None
                print('股东信息不存在...', shareholder_x)

            """对外投资outbound"""
            outbound_x = resp.xpath(outbound_xpath)
            outbound_x = ''.join(outbound_x)
            outbound_x = re.sub('\d', '', outbound_x)
            if outbound_x == '对外投资':
                outbound = self.getoutbound(
                    url='https://www.qcc.com/api/datalist/touzilist',
                    data='keyNo=%s&pageIndex=1' % keyid,
                    keyid=keyid,
                    pageindex=1,
                    new=True,
                )
            else:
                outbound = None
                print('对外投资不存在...')

            if shareholder is None and outbound is None:
                print(f'对外投资， 股东信息都为空，请确定!{url}')
            print(ids)
            qcc_conn.qcc_insert2(litem=ilist, ids=ids, shareholder=shareholder,
                                 investment=outbound, Type=self.type, searchName=search_key)
            qcc_conn.close()

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
    def getshareholder(self, url, data, keyid, new):
        getcookie = self.get_hmac(type=0, keyno=keyid, new=new)
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


class QccXls:
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    """央企+双百+省属企业名单合集"""

    def get_xls_double(self):
        # 打开excel
        wb_list = []
        wb = xlrd.open_workbook('央企+双百+省属企业名单合集-1116.xls')
        # 按工作簿定位工作表
        sh = wb.sheet_by_name('企业名单合集')
        for i in range(sh.nrows):
            data = sh.row_values(i)[3] if re.findall('\d', str(sh.row_values(i)[2])) else sh.row_values(i)[2]
            data = sh.row_values(i)[3] if data == '' else data
            wb_list.append(data)
        return wb_list[1:]

    """AMC及AIC名单.xls"""

    def get_xls_amc(self):
        # 打开excel
        wb_list = []
        wb_list1 = []
        wb_list2 = []
        wb = xlrd.open_workbook('AMC及AIC名单.xls')
        # 按工作簿定位工作表
        sh = wb.sheet_by_name('Sheet1')
        for i in range(sh.nrows):
            data = sh.row_values(i)[1]
            data2 = sh.row_values(i)[2]
            wb_list1.append(data)
            wb_list2.append(data2)
        for i in wb_list1[1:]:
            wb_list.append(i)
        for i in wb_list2[1:]:
            if i:
                wb_list.append(i)
        return wb_list

    """发债主体代码"""

    def get_xls_body(self):
        # 打开excel
        wb_list = []
        wb = xlrd.open_workbook('发债主体代码.xls')
        # 按工作簿定位工作表
        sheetname = ['企业注册情况', '非金融企业债务融资工具', '发改委企业债']
        for name in sheetname:
            sh = wb.sheet_by_name(name)
            for i in range(sh.nrows):
                if i < 1:
                    pass
                else:
                    data = sh.row_values(i)[0]
                    wb_list.append(data)
        return wb_list

    """汽车类上市公司：特力A ~ 大地电气"""

    def get_xls_car(self):
        # 打开excel
        wb_list = []
        # 打开excel
        import csv
        with open('./汽车类上市公司/name.csv', mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            wb = xlrd.open_workbook('汽车类上市公司.xls')
            # 按工作簿定位工作表
            sheetname = ['Sheet1']
            for name in sheetname:
                sh = wb.sheet_by_name(name)
                for i in range(sh.nrows):
                    if i < 1:
                        pass
                    else:
                        data = sh.row_values(i)[1]
                        wb_list.append(data)
        return wb_list

    def xls_main(self):

        num = 0
        for double in set(self.get_xls_double()):
            num += 1
            print(f'央企+双百+省属企业名单合集({num}):', double)
        num = 0
        for amc in set(self.get_xls_amc()):
            num += 1
            print(f'AMC及AIC名单({num}):', amc)
        num = 0
        for bo in set(self.get_xls_body()):
            num += 1
            print(f'发债主体代码({num}):', bo)
        num = 0
        for car in set(self.get_xls_car()):
            num += 1
            print(f'汽车类上市公司({num}):', car)

    def init_mysql(self):
        redisConn = redis_conn()
        redisName = 'qccMainCompany'
        sqlTableName = 'buy_business_qccdata_new'
        key = 'id,level,pid,pageurl,label,credit_code, name,legal_representative,registration_status,status,incorporation_date,registered_capital,paid_capital,organization_code,business_code,taxpayer_code,enterprise_type,business_term,taxpayer_qualification,personnel_size,insured_num,approval_date,area,organ,io_code,industry,english_name,address,business_scope,report_latest,type'
        for i in range(4):
            sql = 'select %s from buy_business_qccdata_copy1 where level=-1 and type="%s"' % (key, i)
            self.cursor.execute(sql)
            finds = self.cursor.fetchall()
            for query in finds:
                name = query[6]
                ids = query[0]
                level = query[1]
                pid = query[2]
                if ids == pid:
                    pid = 'null'
                    query[2] = None

                try:
                    redisbool = redisConn.find_data(field=redisName, value=name)
                    if redisbool:
                        print('*******************************')
                        self.cursor.execute('select id, insertime from %s where name="%s"' % (sqlTableName, name))
                        existFind = self.cursor.fetchone()
                        print('已存在:', name, 'insertime: ', existFind[1])

                        dataid = existFind[0]
                        self.init_relation(i, dataid)
                        print('数据源类型存储成功:', name)
                        self.init_rel(ids, pid, nowid=dataid)
                        print('###############################')

                    else:
                        if int(level) != 1:
                            print('*******************************')
                            pname = self.init_name('buy_business_qccdata_copy1', pid)[1]
                            self.cursor.execute('select id from %s where name="%s"' % (sqlTableName, pname))
                            existFind = self.cursor.fetchone()
                            dataid = existFind[0]
                            query = list(query)
                            query[2] = dataid
                            query = ['null' if i is None else '"' + str(i) + '"' for i in query]
                            query = ','.join(query)
                            sql = 'insert into %s (%s) values (%s)' % (sqlTableName, key, query)
                            self.cursor.execute(sql)
                            self.conn.commit()
                            redisConn.set_add(redisName, value=name)
                            self.init_relation(i, ids)
                            print('插入主表成功:', name)
                            self.init_rel(ids, dataid)
                            print('###############################')
                        else:
                            print('*******************************')
                            sql = 'insert into %s (%s) values (%s)' % (sqlTableName, key, query)
                            self.cursor.execute(sql)
                            self.conn.commit()
                            redisConn.set_add(redisName, value=name)
                            self.init_relation(i, ids)
                            print('插入主表成功:', name)
                            self.init_rel(ids, pid)

                except Exception as e:
                    print('Error_Redis: ', name, e)

    def init_relation(self, eid, dataid):
        """
        :param eid: 类型
        :param dataid: 关联id
        :return:
        """
        if eid == dataid:
            pass
        else:
            try:
                enterprisetype = 'buy_business_qcc_enterprisetype_qccdata'
                enterprisekey = 'enterprisetypeid, dataid'
                enterprisevalue = '%s, %s' % (eid, dataid)
                self.cursor.execute('insert into %s (%s) values (%s)' % (enterprisetype, enterprisekey, enterprisevalue))
                self.conn.commit()
            except:
                pass

    def init_rel(self, cid, pid, nowid=None):
        try:
            print(pid)
            tableName = 'buy_business_qccdata_rel_new'
            if pid == 'null':
                pass
            else:
                if nowid:
                    fon = self.init_name(tableName='buy_business_qccdata_copy1', id=pid)
                    fonname = fon[1]
                    self.cursor.execute('select * from %s where name="%s"' % ('buy_business_qccdata_new', fonname))
                    findid = self.cursor.fetchone()[0]
                    sql = 'insert %s (cid, pid) values ("%s","%s")' % (tableName, nowid, findid)
                    self.cursor.execute(sql)
                    self.conn.commit()
                else:
                    sql = 'insert %s (cid, pid) values ("%s","%s")' % (tableName, cid, pid)
                    self.cursor.execute(sql)
                    self.conn.commit()

        except:
            pass

    def init_name(self, tableName, id):
        """
        :param tableName: 表名
        :param id: 表id索引
        :return: pid, name
        """
        sql = 'select pid, name from %s where id="%s"' % (tableName, id)
        self.cursor.execute(sql)
        finds = self.cursor.fetchone()
        pid = finds[0]
        name = finds[1]
        return pid, name

    def init_errordel(self):
        tableName = 'buy_business_qccdata_new'
        copyName = 'buy_business_qccdata_copy1'
        relName = 'buy_business_qccdata_rel_new'
        typeName = 'buy_business_qcc_enterprisetype_qccdata'
        redisConn = redis_conn()
        sql = 'select * from %s where level = -1 and type=0' % copyName
        self.cursor.execute(sql)
        finds = self.cursor.fetchall()
        for item in finds:
            ids = item[0]
            name = item[7]
            sql = 'select * from %s where name = "%s"' % (tableName, name)
            finds = self.init_search(sql)
            if finds:
                pass
                print('找到:', finds)
            else:
                print('不存在:', name)
                refind = redisConn.find_data('qccMainCompany', name)
                redisConn.del_data('qccMainCompany', name)
                print(refind)

            # relSql = 'delete from %s where cid = %s or pid = %s' % (relName, ids, ids)
            # typeSql = 'delete from %s where dataid = %s' % (typeName, ids)
            # print(self.init_del(tableName, ids))
            # relData = self.init_search(relSql)
            # typeData = self.init_search(typeSql)
            # print(item)
            # print('关系:', relData)
            # print('类型:', typeData)

    def init_search(self, sql):
        self.cursor.execute(sql)
        finds = self.cursor.fetchall()
        return finds

    def init_del(self, tableName, id):
        sql = 'delete from %s where id = %s' %(tableName, id)
        self.cursor.execute(sql)
        self.conn.commit()
        return 'del success TableName: %s  id: %s' % (tableName, id)

    """汽车类上市公司3"""
    def get_xls_data4(self):

        # 打开excel
        import csv
        with open('./汽车类上市公司/name.csv', mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            wb = xlrd.open_workbook('汽车类上市公司.xls')
            # 按工作簿定位工作表
            sheetname = ['Sheet1']
            for name in sheetname:
                sh = wb.sheet_by_name(name)
                for i in range(sh.nrows):
                    if i < 1:
                        pass
                    else:
                        data = sh.row_values(i)[1]
                        sql = 'select gsmc from etm_jbzl where agjc = "%s"' % data
                        self.cursor.execute(sql)
                        result = self.cursor.fetchone()
                        if result:
                            # pass
                            print(list(result))
                            writer.writerow(list(result))
                        else:
                            # notwriter.writerow([data])
                            pass
                            # print('未成功：', data)

                        # name = ''
                        # if result:
                        #     wb_list.append(result[0])
                        #     name = result[0]
                        # else:
                        #     wb_list.append(data)
                        #     name = data
                        #
                        # name = name.replace('(', '（').replace(')', '）')
                        # sql = f'select * from buy_business_qccdata where name like ("%{name}%") and  level=1'
                        # self.cursor.execute(sql)
                        # data = self.cursor.fetchone()
                        # try:
                        #     ids = data[0]
                        #     sql2 = f'select * from buy_business_qccdata where pid ={ids}'
                        #     self.cursor.execute(sql2)
                        #     data2 = self.cursor.fetchall()
                        #     for i in data2:
                        #         level = i[3]
                        #         id2 = i[0]
                        #         a += 1
                        #
                        #         for j in range(len(i)):
                        #             worksheet.write(a, j, i[j])
                        #
                        #         if level==2:
                        #             self.cursor.execute(f'select * from buy_business_qcc_shareholderinformation where id ={id2}')
                        #             data3 = self.cursor.fetchone()
                        #             for j in range(len(data3)):
                        #                 worksheet2.write(a1, j, data3[j])
                        #             a1 += 1
                        #             print(data3)
                        #         if level == 0:
                        #             self.cursor.execute(f'select * from buy_business_qcc_investment where id ={id2}')
                        #             data4 = self.cursor.fetchone()
                        #             print(data4)
                        #             for j in range(len(data4)):
                        #                 worksheet3.write(a2, j, data4[j])
                        #             a2 += 1
                        #     workbook.save('./11.xls')
                        # except:
                        #     pass

        with open('./汽车类上市公司/notname.csv', mode="w", encoding="utf-8-sig", newline="") as f:
            notwriter = csv.writer(f)
            wb = xlrd.open_workbook('汽车类上市公司.xls')
            # 按工作簿定位工作表
            sheetname = ['Sheet1']
            for name in sheetname:
                sh = wb.sheet_by_name(name)
                for i in range(sh.nrows):
                    if i < 1:
                        pass
                    else:
                        data = sh.row_values(i)[1]
                        sql = 'select gsmc from etm_jbzl where agjc = "%s"' % data
                        self.cursor.execute(sql)
                        result = self.cursor.fetchone()
                        if result:
                            pass
                            # print(list(result))
                            # writer.writerow(list(result))
                        else:
                            notwriter.writerow([data])
                            # pass
                            print('未成功：', data)

                        # name = ''
                        # if result:
                        #     wb_list.append(result[0])
                        #     name = result[0]
                        # else:
                        #     wb_list.append(data)
                        #     name = data
                        #
                        # name = name.replace('(', '（').replace(')', '）')
                        # sql = f'select * from buy_business_qccdata where name like ("%{name}%") and  level=1'
                        # self.cursor.execute(sql)
                        # data = self.cursor.fetchone()
                        # try:
                        #     ids = data[0]
                        #     sql2 = f'select * from buy_business_qccdata where pid ={ids}'
                        #     self.cursor.execute(sql2)
                        #     data2 = self.cursor.fetchall()
                        #     for i in data2:
                        #         level = i[3]
                        #         id2 = i[0]
                        #         a += 1
                        #
                        #         for j in range(len(i)):
                        #             worksheet.write(a, j, i[j])
                        #
                        #         if level==2:
                        #             self.cursor.execute(f'select * from buy_business_qcc_shareholderinformation where id ={id2}')
                        #             data3 = self.cursor.fetchone()
                        #             for j in range(len(data3)):
                        #                 worksheet2.write(a1, j, data3[j])
                        #             a1 += 1
                        #             print(data3)
                        #         if level == 0:
                        #             self.cursor.execute(f'select * from buy_business_qcc_investment where id ={id2}')
                        #             data4 = self.cursor.fetchone()
                        #             print(data4)
                        #             for j in range(len(data4)):
                        #                 worksheet3.write(a2, j, data4[j])
                        #             a2 += 1
                        #     workbook.save('./11.xls')
                        # except:
                        #     pass

    """在数据库中根据条件导出子孙公司，数据不全自动补全"""

    def get_data4(self):
        s = outspider()
        import csv
        import xlwt
        book = xlwt.Workbook()
        xlnum = 0
        sh2num = 0
        # 添sheet工作表
        sh1 = book.add_sheet('sheet1')
        sh2 = book.add_sheet('sheet2')
        with open('./汽车类上市公司/name.csv', mode="r", encoding="utf-8-sig", newline="") as f:
            writer = csv.reader(f)
            for queryset in writer:
                fbool = 0
                sql = 'select * from buy_business_qccdata where name ="%s" and pageurl is not null' % queryset[0]. \
                    replace('(', '（').replace(')', '）')
                self.cursor.execute(sql)
                res = self.cursor.fetchone()
                if res:
                    res = list(res)
                    res2 = copy.deepcopy(res)
                    res2[0] = '当前公司'
                    res2[1] = res2[7]
                    print('当前: ', res[7], res[4], res[0])
                    # xlnum += 1
                    # for i in range(len(res2)):
                    #     sh1.write(xlnum, i, res2[i])
                    # xlnum += 1
                    # book.save('./汽车类上市公司/gxtest.xls')
                    s.mains(pageurl=str(res[4]), ids=res[0], name=res[7])
                    reslist = (list(res))
                    id = reslist[0]
                    sons = self.get_son(pid=id)
                    if sons:
                        areaid = '广西'
                        for items in sons:
                            sql = 'select * from buy_business_qccdata where id=%s' % items
                            self.cursor.execute(sql)
                            sonres = self.cursor.fetchone()
                            if res:
                                sonres = list(sonres)
                                sonpageurl = sonres[4]
                                sonid = sonres[0]
                                sonarea = sonres[23]
                                sontypes = sonres[-2]
                                sonlevel = sonres[2]
                                sonname = sonres[7]
                                print('当前子公司:', sonname)
                                if not sonpageurl:
                                    pass
                                    print('子公司数据不完全: ', res)
                                    q = QccSpider(type=type, level=level)
                                    q.start_request(search_key=sonname, id=sonid)
                                else:
                                    if areaid and sonarea:
                                        if areaid in sonarea or areaid in sonname:
                                            fbool += 1
                                            if fbool < 2:
                                                xlnum += 1
                                                for i in range(len(res2)):
                                                    sh1.write(xlnum, i, res2[i])
                                                xlnum += 1
                                                book.save('./汽车类上市公司/gxtest.xls')

                                            print('子公司:', sonname)
                                            # s.mains(pageurl=sonpageurl, ids=sonid, name=sonname)

                                            investment = self.get_investment_new(ids=id, stockname=sonname)
                                            if investment:
                                                investment = list(investment)
                                                investment.append(res2[7])
                                                investment.append('子公司')
                                                print('对外投资:', investment)
                                                # for i in range(len(investment)):
                                                #     sh2.write(sh2num, i, investment[i])
                                                # sh2num += 1
                                                # book.save('./汽车类上市公司/gxtest.xls')

                                            sonres[0] = '子公司'
                                            sonres[1] = sonres[7]

                                            for i in range(len(sonres)):
                                                sh1.write(xlnum, i, sonres[i])
                                            xlnum += 1
                                            book.save('./汽车类上市公司/gxtest.xls')
                                            if not sonpageurl:
                                                print('子公司数据不完全: ', res)
                                                q = QccSpider(type=sontypes, level=sonlevel)
                                                q.start_request(search_key=sonname, id=sonid)
                                        else:
                                            sunquery = self.get_sun(pid=sonid)
                                            if sunquery:
                                                for suni in sunquery:
                                                    sundata = self.qccdata(suni)
                                                    sundata = list(sundata)
                                                    sunidpageurl = sundata[4]
                                                    sunid = sundata[0]
                                                    sunarea = sundata[23]
                                                    sunidtypes = sundata[-2]
                                                    sunidlevel = sundata[2]
                                                    sunidname = sundata[7]
                                                    if not sunidpageurl:
                                                        print('孙公司数据不完全: ', sundata)
                                                        q = QccSpider(type=sunidtypes, level=sunidlevel)
                                                        q.start_request(search_key=sunidname, id=sunid)

                                                    if areaid and sunidname:
                                                        sunarea = sunarea if sunarea else ''
                                                        if areaid in sunidname or areaid in sunarea:
                                                            fbool += 1
                                                            # if fbool < 2:
                                                            #     xlnum += 1
                                                            #     for i in range(len(res2)):
                                                            #         sh1.write(xlnum, i, res2[i])
                                                            #     xlnum += 1
                                                            #     book.save('./汽车类上市公司/gxtest.xls')

                                                            print('孙公司:', sunidname)

                                                            # suninvestment = self.get_investment_new(ids=sonid, stockname=sunidname)
                                                            # if suninvestment:
                                                            #     print('对外投资:', suninvestment)
                                                            #     suninvestment = list(suninvestment)
                                                            #     suninvestment.append(sonname)
                                                            #     suninvestment.append('孙公司')
                                                            #     for i in range(len(suninvestment)):
                                                            #         sh2.write(sh2num, i, suninvestment[i])
                                                            #     sh2num += 1
                                                            #     book.save('./汽车类上市公司/gxtest.xls')

                                                            sundata[0] = '孙公司'
                                                            sundata[1] = sundata[7]
                                                            sundata[2] = '父公司：' + sonname
                                                            s.mains(pageurl=sonpageurl, ids=sonid, name=sonname)
                                                            s.mains(pageurl=sunidpageurl, ids=sunid, name=sunidname)
                                                            # for i in range(len(sundata)):
                                                            #     sh1.write(xlnum, i, sundata[i])
                                                            # xlnum += 1
                                                            # book.save('./汽车类上市公司/gxtest.xls')

                            else:
                                print('子公司不存在: ', id)
                else:
                    print('未成功:', queryset[0])
                    # self.get_data_completion(name=queryset[0], cspider=True)

    '''获取子公司'''

    def get_son(self, pid):
        sql = 'select cid from buy_business_qccdata_rel where pid=%s' % pid
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        res = [i[0] for i in res]
        if res:
            return res
        else:
            return

    '''获取孙公司'''

    def get_sun(self, pid):
        sql = 'select cid from buy_business_qccdata_rel where pid=%s' % pid
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        res = [i[0] for i in res]
        if res:
            return res
        else:
            return

    def qccdata(self, id=None):
        if id:
            sql = 'select * from buy_business_qccdata where id=%s' % id
        else:
            sql = 'select id, pageurl, name from buy_business_qccdata'
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def get_investment_new(self, ids, stockname):
        sql = 'select * from buy_business_qcc_investment_new where id=%s and StockName="%s"' % (ids, stockname)
        self.cursor.execute(sql)
        res = self.cursor.fetchone()
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
        # q = QccSpider(type=types, level=level)
        # q.start_request(search_key=sonname, id=sonid)

    def up2(self, type, level):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        q = QccSpider(type=type, level=level)

        sql01 = f'select * from buy_business_qccdata where type={type} and level={level} and end=1 and pageurl is null'
        self.cursor.execute(sql01)
        r1 = self.cursor.fetchall()
        for i in r1:
            name = i[7].replace('（', '(').replace('）', ')')
            id = i[0]
            code = i[1]
            q.start_request(id=id, search_key=name, cspider=True)

    def up3(self, type, level):
        q = QccSpider(type=type, level=level)
        # sql01 = f'# select * from buy_business_qccdata where id >= 53151 and id <= 53230 and pageurl is null'
        sql01 = f'select * from buy_business_qccdata where type={type} and level=-1 and end=1 and pageurl is null'
        self.cursor.execute(sql01)
        r1 = self.cursor.fetchall()
        for i in r1:
            print(i)
            name = i[7].replace('（', '(').replace('）', ')')
            id = i[0]
            code = i[1]
            q.start_request(search_key=name, id=id, code=code)


if __name__ == '__main__':
    print('''************请注意更新插入等级关系: item['level'] , type************''')

    x = QccXls().init_mysql()
    # x = QccXls().init_errordel()
    # x = QccXls().get_data_completion(sonname='广西上横高速公路有限公司', sonid='53186', types='1', level='-2')
    # x = QccXls().get_data_completion()
    # x = QccXls().get_data4()
    # x = QccXls().get_xls_data4()
    # q = QccSpider(type=type)

    # q.start_request
