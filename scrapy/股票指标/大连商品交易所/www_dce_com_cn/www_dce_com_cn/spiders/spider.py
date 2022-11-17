# http://www.dce.com.cn/dalianshangpin/xqsj/tjsj26/rtj/rxq/index.html
import scrapy
from fake_useragent import UserAgent
from ..data_process import *
from ..redis_conn import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    year = weekday_1('2022-08-30', Y=True)
    month = weekday_1('2022-08-30', M=True)
    day = weekday_1('2022-08-30', D=True)
    datenow = weekday_1('2022-08-30')
    config = {'condition': True}

    def start_requests(self):
        for query in range(len(self.year)):
            year = self.year[query]
            month = int(self.month[query]) - 1
            day = self.day[query]
            daynow = self.datenow[query]
            url = 'http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
            data = f'dayQuotes.variety=all&dayQuotes.trade_type=0&year={year}&month={month}&day={day}'
            headers = {'User-Agent': UserAgent().random,
                       'Content-Type': 'application/x-www-form-urlencoded'}
            if self.config['condition'] is True:
                yield scrapy.Request(url=url, body=data, headers=headers, method='POST', callback=self.lparse,
                                     meta={'datenow': daynow})
            else:
                break

    def lparse(self, response):
        item = {}
        PRODUCTNAME = response.xpath("//div[@class='dataArea']//tr/td[1]//text()").getall()  # 商品名称
        Delivery_month = response.xpath("//div[@class='dataArea']//tr/td[2]//text()").getall()  # 交割月份
        OPENPRICE = response.xpath("//div[@class='dataArea']//tr/td[3]//text()").getall()  # 开盘价
        HIGHESTPRICE = response.xpath("//div[@class='dataArea']//tr/td[4]//text()").getall()  # 最高价
        LOWESTPRICE = response.xpath("//div[@class='dataArea']//tr/td[5]//text()").getall()  # 最低价
        CLOSEPRICE = response.xpath("//div[@class='dataArea']//tr/td[6]//text()").getall()  # 收盘价
        SETTLEMENTPRICE = response.xpath("//div[@class='dataArea']//tr/td[8]//text()").getall()  # 结算价
        PRESETTLEMENTPRICE = response.xpath("//div[@class='dataArea']//tr/td[7]//text()") .getall()  # 昨结算价
        ZD1_CHG = response.xpath("//div[@class='dataArea']//tr/td[9]//text()").getall()  # 涨跌1
        ZD2_CHG = response.xpath("//div[@class='dataArea']//tr/td[10]//text()").getall()  # 涨跌2
        VOLUME = response.xpath("//div[@class='dataArea']//tr/td[11]//text()").getall()  # 成交量
        TURNOVER = response.xpath("//div[@class='dataArea']//tr/td[14]//text()").getall()  # 成交额
        OPENINTEREST = response.xpath("//div[@class='dataArea']//tr/td[12]//text()").getall()  # 持仓量
        OPENINTERESTCHG = response.xpath("//div[@class='dataArea']//tr/td[13]//text()").getall()  # 持仓量变化

        for query in range(len(PRODUCTNAME)):
            DATE = response.meta['datenow']  # 日期
            EXCHANGE_PLACE = '大连商品交易所'  # 交易所

            item['DATE'] = DATE
            item['EXCHANGE_PLACE'] = EXCHANGE_PLACE
            item['PRODUCTNAME'] = process_text(PRODUCTNAME[query])
            item['OPENPRICE'] = process_text(OPENPRICE[query])
            item['LOWESTPRICE'] = process_text(LOWESTPRICE[query])
            item['HIGHESTPRICE'] = process_text(HIGHESTPRICE[query])
            item['CLOSEPRICE'] = process_text(CLOSEPRICE[query])
            item['SETTLEMENTPRICE'] = process_text(SETTLEMENTPRICE[query])
            item['PRESETTLEMENTPRICE'] = process_text(PRESETTLEMENTPRICE[query])
            item['ZD1_CHG'] = process_text(ZD1_CHG[query])
            item['ZD2_CHG'] = process_text(ZD2_CHG[query])
            item['VOLUME'] = process_text(VOLUME[query])
            item['TURNOVER'] = process_text(TURNOVER[query])
            item['OPENINTEREST'] = process_text(OPENINTEREST[query])
            item['OPENINTERESTCHG'] = process_text(OPENINTERESTCHG[query])
            item['pageurl'] = response.url

            if '小计' in item['PRODUCTNAME'] or '总计' in item['PRODUCTNAME']:
                pass
            else:
                item['CONTRACT_CODE'] = process_text(PRODUCTNAME[query]) + process_text(Delivery_month[query])  # 合约代码
                conn = redis_conn()
                redis_key = item['pageurl'] + item['CONTRACT_CODE']  # 去重配置： 链接+合约代码
                redis_key = encrypt_md5(redis_key)
                result = conn.find_data(value=redis_key)
                if result is False:
                    yield item
                else:
                    self.config['condition'] = False
                    print('存在：', redis_key)

