# https://www.shfe.com.cn/statements/dataview.html?paramid=kx
import scrapy, copy
from scrapy import cmdline
from ..data_process import *
from ..redis_conn import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_date = '20220830'
    date_list = weekday_1(start_date)
    config = {'condition': True}

    def start_requests(self):
        for date in self.date_list:
            starf_date = date.replace('-', '')
            url = f'https://www.shfe.com.cn/data/dailydata/kx/kx{starf_date}.dat'
            if self.config['condition'] is True:
                yield scrapy.Request(url=url, callback=self.lparse, meta={'date': date})
            else:
                break

    def lparse(self, response):
        item = {}
        lresult = response.json()
        o_curinstrument = lresult.get('o_curinstrument', None)
        for query in o_curinstrument:
            DATE = response.meta['date']  # 日期
            EXCHANGE_PLACE = '上海期货交易所'  # 交易所
            DELIVERYMONTH = query.get('DELIVERYMONTH', None)  # 交割月份
            PRODUCTNAME = query.get('PRODUCTNAME', None).strip()  # 商品名称
            CONTRACT_CODE = PRODUCTNAME + DELIVERYMONTH  # 合约代码
            OPENPRICE = query.get('OPENPRICE', None)  # 开盘价
            HIGHESTPRICE = query.get('HIGHESTPRICE', None)  # 最高价
            LOWESTPRICE = query.get('LOWESTPRICE', None)  # 最低价
            CLOSEPRICE = query.get('CLOSEPRICE', None)  # 收盘价
            SETTLEMENTPRICE = query.get('SETTLEMENTPRICE', None)  # 结算价
            PRESETTLEMENTPRICE = query.get('PRESETTLEMENTPRICE', None)  # 昨结算价
            ZD1_CHG = query.get('ZD1_CHG', None)  # 涨跌1
            ZD2_CHG = query.get('ZD2_CHG', None)  # 涨跌2
            VOLUME = query.get('VOLUME', None)  # 成交量
            TURNOVER = query.get('TURNOVER', None)  # 成交额
            OPENINTEREST = query.get('OPENINTEREST', None)  # 持仓量
            OPENINTERESTCHG = query.get('OPENINTERESTCHG', None)  # 持仓量变化

            item['DATE'] = DATE
            item['EXCHANGE_PLACE'] = EXCHANGE_PLACE
            item['PRODUCTNAME'] = PRODUCTNAME
            item['OPENPRICE'] = OPENPRICE
            item['CONTRACT_CODE'] = CONTRACT_CODE
            item['LOWESTPRICE'] = LOWESTPRICE
            item['HIGHESTPRICE'] = HIGHESTPRICE
            item['CLOSEPRICE'] = CLOSEPRICE
            item['SETTLEMENTPRICE'] = SETTLEMENTPRICE
            item['PRESETTLEMENTPRICE'] = PRESETTLEMENTPRICE
            item['ZD1_CHG'] = ZD1_CHG
            item['ZD2_CHG'] = ZD2_CHG
            item['VOLUME'] = VOLUME
            item['TURNOVER'] = TURNOVER
            item['OPENINTEREST'] = OPENINTEREST
            item['OPENINTERESTCHG'] = OPENINTERESTCHG
            item['pageurl'] = response.url

            if '小计' in item['PRODUCTNAME'] or '总计' in item['PRODUCTNAME'] or '原油TAS' in item['PRODUCTNAME'] or '小计' in item['CONTRACT_CODE']:
                pass
            else:
                conn = redis_conn()
                redis_key = item['pageurl'] + item['CONTRACT_CODE']  # 去重配置： 链接+合约代码
                redis_key = encrypt_md5(redis_key)
                result = conn.find_data(value=redis_key)
                if result is False:
                    yield item
                else:
                    self.config['condition'] = False
                    print('存在：', redis_key)


