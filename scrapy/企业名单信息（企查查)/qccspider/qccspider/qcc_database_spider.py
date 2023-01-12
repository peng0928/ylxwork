# -*- coding: utf-8 -*-
# @Date    : 2022-10-26 17:13
# @Author  : chenxuepeng
import copy
import math
import json
import logging
import os
import re
import requests
from lxml import etree
from decorator_penr import *
from qcc_hmac import *
from useragent import *
from qcc_database_mysql import *
from redis_conn import *
from data_process import *
from qcc_outspider import outspider
from config import *


class QccSpider():

    def __init__(self):
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

    @retry(exceptions=True, max_retries=15)
    def start_request(self, *args, **kwargs):
        search_key = kwargs.get('name')
        self.TYPE = kwargs.get('TYPE')
        self.LEVEL = kwargs.get('LEVEL')
        search_id = kwargs.get('ID')
        self.notfound = {}
        self.nottag = []
        '''数据查询去重-去除重复采购单位'''
        headers = {}
        headers.update({"User-Agent": get_ua()})
        headers.update({"cookie": self.open_cookie()})
        condition = True  # False：在企查查中匹配到数据; Ture:在企查查未匹配到数据

        search_url = f'https://www.qcc.com/web/search?key={search_key}'
        response = requests.get(search_url, headers=headers, proxies={
            'https': 'tps163.kdlapi.com:15818'})
        response.encoding = 'utf-8'
        '''状态码判断'''
        if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
            error_msg = re.findall('(<title>.*?</title>)', response.text)[0]
            raise ValueError('异常请求, 请求失败===>>>', search_url)

        else:
            tree = etree.HTML(response.text)
            maininfo = tree.xpath(maininfoXpath)
            numi = 0
            for item in maininfo:
                if condition is True:
                    company_names = item.xpath(company_namesXpath)
                    company_names = ''.join(company_names)
                    # cc = opencc.OpenCC('t2s')
                    # company_name = cc.convert(company_names.replace('（', '(').replace('）', ')')) # 企业名称：繁体转简体
                    company_name = company_names
                    curl = item.xpath(curlXpath)[0]
                    tags = item.xpath(tagsXpath)
                    tags = tags if tags else '-'
                    tags = [i.strip() for i in tags]
                    tags = ','.join(tags)
                    numi += 1
                    print(numi, company_name, search_key)
                    d = {company_name: curl}
                    self.notfound[numi] = d
                    self.nottag.append(tags)
                    if company_name == search_key:
                        self.cspider(curl, tags, search_key, search_id)
                        condition = False
                else:
                    break
            '''企查查未找到'''
            if condition is True:
                print(self.notfound)
                sinput = 'q'
                if sinput != 'q':
                    sname = self.notfound.get(int(sinput))
                    for k, v in sname.items():
                        self.cparse(
                            v, self.nottag[int(sinput)], search_key)
                else:
                    self.logger.info(f'Not Found:名称 {search_key}')

    @retry(exceptions=True, max_retries=10)
    def cspider(self, url, tags, search_key, ids):
        """
        :
        :parmes url: 网站链接
        """
        headers = {}
        headers.update({"User-Agent": get_ua()})
        headers.update({"cookie": self.open_cookie()})
        redisConn = redis_conn()
        qcc_conn = pymysql_connection()
        keyid = re.findall('firm/(.*?)\.html', url)
        keyid = keyid[0] if keyid else keyid
        item = {}
        response = requests.get(url, headers=headers, proxies={
                                'https': 'tps163.kdlapi.com:15818'}, timeout=3)
        if '公司不存在' in response.text:
            raise ValueError(f'{search_key}公司不存在:{url}')

        elif str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
            raise ValueError('异常访问,访问失败===>>>', search_key, url)

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
                        v_text = ''.join(v_text).replace(
                            '\n', '').strip() if v_text else v_text
                        v_text = ''.join(v_text.split())
                        value_list.append(v_text)

                len_k = len(qcc_key)
                len_v = len(value_list)

                if len_k != len_v:
                    raise ValueError('字段长度不匹配, 请重新检测网站===>>>', url)
                else:
                    for i in range(len_k):
                        item[qcc_key[i]] = value_list[i]
            item['参保人数'] = item.get('参保人数').replace(
                '趋势图', '') if item.get('参保人数') else item.get('参保人数')
            item['网站链接'] = url
            item['type'] = str(self.TYPE)
            item['企业标签'] = tags if tags else 'null'
            sql_key_list = []
            sql_value_list = []
            item['level'] = str(self.LEVEL)
            for k, v in item.items():
                ak = self.qcc_item_dict.get(k)
                if ak and v:
                    sql_key_list.append(ak)
                    sql_value_list.append(
                        v.replace('"', '“').replace(',', '，'))
            sql_key = ','.join(sql_key_list)
            sql_value_list = ['"' + str(i) + '"' for i in sql_value_list]
            sql_value = ','.join(sql_value_list)
            ilist = []
            for i in range(len(sql_key_list)):
                ilist.append(sql_key_list[i] + '=' + sql_value_list[i])
            ilist = ','.join(ilist)

            """工商数据"""
            print('工商数据获取成功;', search_key, url)

            # shareholderBool = False
            # investmentBool = False
            # datatab = resp.xpath(datatabXpath)
            # for query in datatab:
            #     query = query.strip()
            #     if '股东信息' in query:
            #         shareholderNum = re.findall('\d+', query)
            #         shareholderNum = int(
            #             shareholderNum[0]) if shareholderNum else None
            #         if shareholderNum and shareholderNum > 0:
            #             shareholderBool = True

            #     if '对外投资' in query:
            #         investmentNum = re.findall('\d+', query)
            #         investmentNum = int(
            #             investmentNum[0]) if investmentNum else None
            #         if investmentNum and investmentNum > 0:
            #             investmentBool = True

            # redsi_name = str(ids) + '_' + search_key
            # RedisShareholder = redisConn.find_data(
            #     field='qcc_shareholderinformation_new', value=redsi_name)

            # Redisinvestment = redisConn.find_data(
            #     field='qcc_investment_new', value=redsi_name)

            # if RedisShareholder is True:
            #     print('\033[2;32m股东信息已存在\033[0m')
            # else:
            #     """股东信息"""
            #     if shareholderBool is False:
            #         shareholder = None
            #         print(f'股东信息获取失败;')
            #     else:
            #         shareholder_new = resp.xpath(
            #             "//section[@id='partner']//span[@class='tab-item'][1]//span[@class='item-title']/text()")
            #         shareholder_new = shareholder_new[0] if shareholder_new else ''
            #         if shareholder_new == '最新公示':
            #             shareholder = self.getshareholder(
            #                 url='https://www.qcc.com/api/datalist/partner',
            #                 data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi&type=IpoPartners' % keyid,
            #                 keyid=keyid,
            #                 new=True,
            #             )
            #         else:
            #             shareholder = self.getshareholder(
            #                 url='https://www.qcc.com/api/datalist/partner',
            #                 data='isSortAsc=true&keyNo=%s&pageIndex=1&pageSize=50&sortField=shouldcapi' % keyid,
            #                 keyid=keyid,
            #                 new=False,
            #             )
            #         print('\033[3;32m股东信息获取成功;\033[0m', shareholder)

            # """对外投资investment"""
            # if Redisinvestment is True:
            #     print('\033[2;32m对外投资已存在\033[0m')
            # else:
            #     if investmentBool is False:
            #         investment = None
            #         print('对外投资获取失败;')
            #     else:
            #         investment = self.getinvestment(
            #             url='https://www.qcc.com/api/datalist/touzilist',
            #             data='keyNo=%s&pageIndex=1' % keyid,
            #             keyid=keyid,
            #             pageindex=1,
            #             new=True,
            #         )
            #         print('\033[2;32m对外投资获取成功;\033[0m', investment)

            qcc_conn.qccUpdate(litem=ilist, ids=ids, shareholder=None,
                               investment=None, Type=self.TYPE, searchName=search_key)
            qcc_conn.close()

    def log(self):
        os.makedirs('./loging', exist_ok=True)
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("./loging/log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        response = requests.get(url=url, headers=headers, proxies={
                                'https': 'tps163.kdlapi.com:15818'}, timeout=1)
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

    def get_hmac(self, type=0, keyno=None,  new=None, pageindex=None):
        """
        :param keyno: 公司唯一标识：b8d99d133f16f34f30f7224145d8ec6f(https://www.qcc.com/firm/b8d99d133f16f34f30f7224145d8ec6f.html)
        :param tid: window.tid
        :return: 0: 股权穿透图子集, 1: 股权穿透图父集
        """
        tid = TID
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
                print(f'正在获取股东信息:{code}, 数量:',
                      response.json().get('pageInfo').get('total'))
                for qdata in datas:
                    item_dict = {}
                    StockName = qdata.get('StockName', '-')  # 股东及出资信息
                    ShareType = qdata.get('ShareType', '-')  # 股份类型
                    StockPercent = qdata.get('StockPercent', '-')  # 持股比例
                    ShouldCapi = qdata.get('TotalShouldAmount', '-')  # 持股数(股)
                    RegistCapi = qdata.get('RegistCapi', '-')  # 认缴出资额(万元)
                    ShoudDate = qdata.get('ShoudDate', '-')  # 认缴出资日期
                    ShoudDate = ShoudDate if ShoudDate else '-'
                    ShoudDate = ShoudDate.split(
                        ',')[-1] if ',' in ShoudDate else ShoudDate
                    FinalBenefitPercent = qdata.get(
                        'FinalBenefitPercent', '-')  # 最终受益股份
                    InDate = qdata.get('InDate', '-')  # 首次持股日期
                    Name = qdata.get('Product')  # 关联产品/机构
                    ProductName = Name.get(
                        'Name', '-') if Name else '-'  # 关联产品/机构
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
                input("\033[1;32m请验证账号: %s\033[0m" % url)
                raise ValueError("请验证账号:")

    @retry(delay=2, exceptions=True, max_retries=5)
    def getinvestment(self, url=None, data=None, keyid=None, new=None, pageindex=None):
        getcookie = self.get_hmac(type=1, keyno=keyid, pageindex=pageindex)
        header = copy.deepcopy(self.headers_data)
        header.update(getcookie)
        item_list = []
        response = requests.get(url=url, headers=header, params=data)
        code = response.status_code
        try:
            datas = response.json().get('data')
            if datas:
                page = math.ceil(response.json().get(
                    'pageInfo').get('total') / 10)
                page = int(page)
                print(f'正在获取对外投资信息:{code}, 页数:', page)
                for qdata in datas:
                    item_dict = {}
                    Name = qdata.get('Name', '-')  # 被投资企业名称
                    Status = qdata.get('Status', '-')  # 状态
                    StartDate = qdata.get('StartDate')  # 成立日期
                    FundedRatio = qdata.get('FundedRatio', '-')  # 持股比例
                    ShouldCapi = qdata.get('ShouldCapi', '-')  # 认缴出资额/持股数
                    ProvinceName = qdata.get('ProvinceName', '-')  # 所属省份
                    IndustryItem = qdata.get('IndustryItem')  # 所属行业
                    Industry = IndustryItem.get(
                        'Industry') if IndustryItem else '-'  # 所属行业
                    Product = qdata.get('Product')  # 关联产品/机构
                    ProductName = Product.get(
                        'Name') if Product else '-'  # 关联产品/机构
                    item_dict['Status'] = Status
                    item_dict['StartDate'] = StartDate
                    item_dict['FundedRatio'] = FundedRatio
                    item_dict['ShouldCapi'] = ShouldCapi
                    item_dict['ProvinceName'] = ProvinceName
                    item_dict['Industry'] = Industry
                    item_dict['ProductName'] = ProductName
                    item_dict['StockName'] = Name
                    item_list.append(item_dict)

                if page > 1:
                    for i in range(2, page + 1):
                        print(f'正在抓取第{i}页.')
                        outbound = self.getinvestment2(
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
                input("\033[1;33m请验证账号: %s\033[0m" % url)
                raise ValueError("请验证账号:")

    @retry(delay=2, exceptions=True, max_retries=5)
    def getinvestment2(self, url=None, data=None, keyid=None, new=None, pageindex=None):
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
                    Name = qdata.get('Name', '-')  # 被投资企业名称
                    Status = qdata.get('Status', '-')  # 状态
                    StartDate = qdata.get('StartDate', '-')  # 成立日期
                    FundedRatio = qdata.get('FundedRatio', '-')  # 持股比例
                    ShouldCapi = qdata.get('ShouldCapi', '-')  # 认缴出资额/持股数
                    ProvinceName = qdata.get('ProvinceName', '-')  # 所属省份
                    IndustryItem = qdata.get('IndustryItem')  # 所属行业
                    Industry = IndustryItem.get(
                        'Industry') if IndustryItem else '-'  # 所属行业
                    Product = qdata.get('Product')  # 关联产品/机构
                    ProductName = Product.get(
                        'Name') if Product else '-'  # 关联产品/机构
                    item_dict['Status'] = Status
                    item_dict['StartDate'] = StartDate
                    item_dict['FundedRatio'] = FundedRatio
                    item_dict['ShouldCapi'] = ShouldCapi
                    item_dict['ProvinceName'] = ProvinceName
                    item_dict['Industry'] = Industry
                    item_dict['ProductName'] = ProductName
                    item_dict['StockName'] = Name
                    item_list.append(item_dict)
                return item_list
        except Exception as e:
            if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                print('对外投资失败:', code, e)
                input("\033[1;33m请验证账号: %s\033[0m" % url)
                raise ValueError("请验证账号:")


class QccMainRun:
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.redisConn = redis_conn()

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

    def init_search(self, sql):
        self.cursor.execute(sql)
        finds = self.cursor.fetchall()
        return finds

    def init_del(self, tableName, id):
        sql = 'delete from %s where id = %s' % (tableName, id)
        self.cursor.execute(sql)
        self.conn.commit()
        return 'del success TableName: %s  id: %s' % (tableName, id)

    """汽车类上市公司3"""

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

    def get_investment_new(self, ids, stockname):
        sql = 'select * from buy_business_qcc_investment_new where id=%s and StockName="%s"' % (
            ids, stockname)
        self.cursor.execute(sql)
        res = self.cursor.fetchone()
        return res
    """更新数据库空缺子公司数据启动入口，补全：工商数据，对外招标，股东信息"""

    def main(self, level=None):
        QCC = QccSpider()
        mainTable = 'buy_business_qccdata_new'
        mainRedisName = 'qccMainCompany'
        mainKey = 'id,level,pid,pageurl,label,credit_code, name,legal_representative,registration_status,status,incorporation_date,registered_capital,paid_capital,organization_code,business_code,taxpayer_code,enterprise_type,business_term,taxpayer_qualification,personnel_size,insured_num,approval_date,area,organ,io_code,industry,english_name,address,business_scope,report_latest,type'
        selectEmpty = 'select * from %s where level = %s and pageurl is null ' % (
            mainTable, level)
        self.cursor.execute(selectEmpty)
        queryResults = list(self.cursor.fetchall())
        queryResultNum = len(queryResults)
        print('当前级别:', level, '总数量:', queryResultNum)
        num = 0
        for query in queryResults:
            num += 1
            startTIME = datetime.datetime.now()
            print(
                f"**********************************************************************{num}")
            nowID = query[0]
            nowLEVEL = query[1]
            nowPID = query[2]
            nowNAME = query[6]
            nowTYPE = query[-2]
            print('\033[1;32m当前公司:', nowNAME, 'ID:', nowID, 'PID:',
                  nowPID, 'TYPE:', nowLEVEL, 'LEVEL:', nowLEVEL, '开始时间:', startTIME, '\033[0m')
            QCC.start_request(name=nowNAME, ID=nowID,
                              TYPE=nowTYPE, LEVEL=nowLEVEL)
            print(
                "######################################################################\n")


if __name__ == '__main__':
    print('\033[3;32m'+tipMSG+'\033[0m')
    Penr = QccMainRun().main(level=0)
