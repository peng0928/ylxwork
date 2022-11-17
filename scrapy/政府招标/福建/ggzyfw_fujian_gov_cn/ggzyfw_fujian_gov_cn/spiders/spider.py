import scrapy, json
from ..encryptions import *
from ..redis_conn import *
from ..data_process import *
from ..AES_CBC_256 import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzyfw.fujian.gov.cn'
    condition = True

    def start_requests(self):
        lurl = 'https://ggzyfw.fujian.gov.cn/FwPortalApi/Trade/TradeInfo'
        timenow = str(timestamp())
        start_time = get_datetime_now()
        end_time = get_datetime_now(reduce_months=6)
        pages = [525, 35, 453, 446, 30, 368, 431, 28, 359, 119, 12, 105]
        p = 0
        for GGTYPE in range(1, 5):
            for PROTYPE in range(1, 4):
                getpage = pages[p]
                p += 1
                for page in range(1, getpage):
                    data = '{"pageNo":%s,"pageSize":20,"total":10382,"AREACODE":"","M_PROJECT_TYPE":"","KIND":"ZFCG","GGTYPE":"%s","PROTYPE":"D0%s","timeType":"6","BeginTime":"%s 00:00:00","EndTime":"%s 23:59:59","createTime":[],"ts":%s}' % (page, GGTYPE, PROTYPE, end_time, start_time, timenow)
                    portal_sign_word = '3637CB36B2E54A72A7002978D0506CDFBeginTime%s 00:00:00createTime[]EndTime%s 23:59:59GGTYPE%sKINDZFCGpageNo%spageSize20PROTYPED0%stimeType6total10382ts%s' % (end_time, start_time, GGTYPE, page, PROTYPE, timenow)
                    portal_sign = md5(portal_sign_word)
                    headers = {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Connection": "keep-alive",
                        "Content-Type": "application/json;charset=UTF-8",
                        "Host": "ggzyfw.fujian.gov.cn",
                        "Origin": "https://ggzyfw.fujian.gov.cn",
                        "portal-sign": f"{portal_sign}",
                        "Referer": "https://ggzyfw.fujian.gov.cn/business/list",
                        "sec-ch-ua-mobile": "?0",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
                    }
                    if self.condition is True:
                        yield scrapy.Request(url=lurl, body=data, callback=self.lparse, headers=headers, method='POST')
                    else:
                        break

    def lparse(self, response):
        conn = redis_conn()
        timenow = str(timestamp())
        key = 'BE45D593014E4A4EB4449737660876CE'
        iv = 'A8909931867B0425'
        data = response.json().get('Data', None)
        aes_data = AesCrypto(key=key, iv=iv).decrypt(data)
        data_json = json.loads(aes_data).get('Table', None)
        for item in data_json:
            curl = 'https://ggzyfw.fujian.gov.cn/FwPortalApi/Trade/TradeInfoContent'
            M_ID = item.get('M_ID', None)
            # M_ID = '230215'
            NAME = item.get('NAME', None)
            TM1 = item.get('TM1', None)
            lurl = curl + '?' + str(M_ID)
            meta = {'NAME': NAME, 'TM1': TM1, 'lurl': lurl}
            cdata = '{"m_id":%s,"type":"PURCHASE_QUALI_INQUERY_ANN","ts":%s}' % (M_ID, timenow)
            portal_sign_word = '3637CB36B2E54A72A7002978D0506CDFm_id%sts%stypePURCHASE_QUALI_INQUERY_ANN' % (M_ID, timenow)
            portal_sign = md5(portal_sign_word)
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "Host": "ggzyfw.fujian.gov.cn",
                "Origin": "https://ggzyfw.fujian.gov.cn",
                "portal-sign": f"{portal_sign}",
                "Referer": "https://ggzyfw.fujian.gov.cn/business/list",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
            }

            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=curl, body=cdata, callback=self.cparse, headers=headers, method='POST', meta=meta)
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        # print(response.meta['NAME'])
        item = {}
        key = 'BE45D593014E4A4EB4449737660876CE'
        iv = 'A8909931867B0425'
        data = response.json().get('Data', None)
        aes_data = AesCrypto(key=key, iv=iv).decrypt(data)
        Contents = json.loads(aes_data).get('Contents', None)
        Contents = Contents.replace('&nbsp;', '') if Contents else Contents
        content_result = process_content_type(C=Contents)
        item['host'] = self.host
        item['pageurl'] = response.meta['lurl']
        item['docsubtitle'] = response.meta['NAME']
        item['publishdate'] = response.meta['TM1']
        item['contenttype'] = content_result
        item['pagesource'] = Contents
        yield item
        # print(item)