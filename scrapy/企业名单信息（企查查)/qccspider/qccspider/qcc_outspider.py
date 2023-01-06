# -*- coding: utf-8 -*-
# @Date    : 2023-01-06 15:53
# @Author  : chenxuepeng
from decorator_penr import *
from redis_conn import *
import requests, math, re, json
from qcc_hmac import *
from useragent import *
import pymysql

class outspider():
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.i = 1
        self.ua = get_ua()
        self.headers_data = {
            "content-type": "application/json",
            "cookie": self.open_cookie('cookie_data'),
            'user-agent': get_ua(),
        }

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

    def mains(self, pageurl, ids, name):
        conn = redis_conn()
        field = 'qcc_outbound'
        findres = conn.find_data(field=field, value=name)
        if findres is False:
            """对外投资outbound"""
            keyid = re.findall('firm/(.*?)\.html', pageurl)
            keyid = keyid[0] if keyid else keyid
            try:
                outbound = self.getoutbound(
                    url='https://www.qcc.com/api/datalist/touzilist',
                    data='keyNo=%s&pageIndex=1' % keyid,
                    keyid=keyid,
                    pageindex=1,
                    new=True,
                )
                self.data_save(items=outbound, ids=ids)
                conn.set_add(field=field, value=name)
            except:
                pass
        else:
            print('已存在: ', name)

    def data_save(self, items=None, ids=None):
        for l in items:
            str_k = ''
            str_v = ''
            for k, v in l.items():
                str_k += f"{k}" + ','
                str_v += f'"{v}"' + ','
            str_k += 'id'
            str_v += f'{ids}'
            shareholder_sql = 'insert into %s (%s) values (%s)' % ('buy_business_qcc_investment_new', str_k, str_v)
            self.cursor.execute(shareholder_sql)
            self.conn.commit()

if __name__ == '__main__':
    s = outspider().mains(pageurl='https://www.qcc.com/firm/5dffb644394922f9073544a08f38be9f.html', ids='53138', name='1')
