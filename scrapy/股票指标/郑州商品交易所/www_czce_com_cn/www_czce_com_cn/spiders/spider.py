# http://www.czce.com.cn/cn/jysj/mrhq/H770301index_1.htm
import scrapy
from ..data_process import *
from ..weekday import *
from ..redis_conn import *

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    dic = {
        'CF': '棉花CF', "SR": '白糖SR', "TA": 'PTA', "OI": '菜油OI', "RI": '早籼RI', "WH": '强麦WH',
        "FG": '玻璃FG', "PM": '普麦PM', "RS": '油菜籽RS', "RM": '菜籽粕RM', "ZC": '动力煤ZC',
        "JR": '粳稻JR', "MA": '甲醇MA', "LR": '晚籼LR', "SF": '硅铁SF', "SM": '锰硅SM', "CY": '棉纱CY',
        "AP": '苹果AP', "CJ": '红枣CJ', "UR": '尿素UR',
        "SA": '纯碱SA', "PF": '短纤PF', "PK": '花生PK',
    }
    config = {'condition': True}
    def start_requests(self):
        for date in weekday_1(start_date='2020-08-30'):
            datenormal = date.strftime('%Y-%m-%d')
            datenow = date.strftime('%Y%m%d')
            year = date.strftime('%Y')
            url = f'http://www.czce.com.cn/cn/DFSStaticFiles/Future/{year}/{datenow}/FutureDataDaily.htm'
            if self.config['condition'] is True:
                yield scrapy.Request(url=url, callback=self.lparse, meta={'datenormal': datenormal})
            else:
                break

    def lparse(self, response):
        item = {}
        DATE = response.meta['datenormal']  # 日期
        EXCHANGE_PLACE = '郑州商品交易所'  # 交易所
        CONTRACT_CODE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[1]")  # 合约代码
        OPENPRICE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[3]")  # 开盘价
        HIGHESTPRICE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[4]")  # 最高价
        LOWESTPRICE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[5]")  # 最低价
        CLOSEPRICE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[6]")  # 收盘价
        SETTLEMENTPRICE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[7]")  # 结算价
        PRESETTLEMENTPRICE = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[2]")  # 昨结算价
        ZD1_CHG = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[8]")  # 涨跌1
        ZD2_CHG = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[9]")  # 涨跌2
        VOLUME = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[10]")  # 成交量
        TURNOVER = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[13]")  # 成交额
        OPENINTEREST = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[11]")  # 持仓量
        OPENINTERESTCHG = response.xpath("//div[@class='date_box3']//tbody//tr[position()>-1]/td[12]")  # 持仓量变化

        for query in range(len(OPENPRICE)):
            # item['DATE'] = DATE[query].xpath('.//text()').get()
            item['CONTRACT_CODE'] = process_text(CONTRACT_CODE[query].xpath('.//text()').get())
            PRODUCTNAME = re.findall('[A-Z]+', item['CONTRACT_CODE'])
            if PRODUCTNAME:
                PRODUCTNAME = self.dic.get(PRODUCTNAME[0], None)
            else:
                PRODUCTNAME = None
            item['OPENPRICE'] = process_text(OPENPRICE[query].xpath('.//text()').get())
            item['LOWESTPRICE'] = process_text(LOWESTPRICE[query].xpath('.//text()').get())
            item['HIGHESTPRICE'] = process_text(HIGHESTPRICE[query].xpath('.//text()').get())
            item['CLOSEPRICE'] = process_text(CLOSEPRICE[query].xpath('.//text()').get())
            item['SETTLEMENTPRICE'] = process_text(SETTLEMENTPRICE[query].xpath('.//text()').get())
            item['PRESETTLEMENTPRICE'] = process_text(PRESETTLEMENTPRICE[query].xpath('.//text()').get())
            item['ZD1_CHG'] = process_text(ZD1_CHG[query].xpath('.//text()').get())
            item['ZD2_CHG'] = process_text(ZD2_CHG[query].xpath('.//text()').get())
            item['VOLUME'] = process_text(VOLUME[query].xpath('.//text()').get())
            item['TURNOVER'] = process_text(TURNOVER[query].xpath('.//text()').get())
            item['OPENINTEREST'] = process_text(OPENINTEREST[query].xpath('.//text()').get())
            item['OPENINTERESTCHG'] = process_text(OPENINTERESTCHG[query].xpath('.//text()').get())
            item['PRODUCTNAME'] = PRODUCTNAME
            item['EXCHANGE_PLACE'] = EXCHANGE_PLACE
            item['DATE'] = DATE
            item['pageurl'] = response.url
            if '小计' in item['CONTRACT_CODE'] or '总计' in item['CONTRACT_CODE']:
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
                    print(self.config['condition'])
