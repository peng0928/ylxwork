import scrapy, os, logging, json
from ..data_process import *
from ..redis_conn import *
from ..useragent import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    type_id = {'工程建设': 0, '政府采购': 1, '土地使用权': 2, '矿业权': 3, '国有产权': 4,
               '碳排放权': 5, '排污权': 6, '药品采购': 7, '二类疫苗': 8, '林权': 9, '其他': 10,
               }
    endtime = get_datetime_now()
    startdate = get_datetime_now(reduce_months=3)
    host = 'www.ggzy.gov.cn'
    condition = True

    def start_requests(self):
        pages = [60833, 6242]
        for i in range(2):
            for page in range(1, pages[i]):
                datas = [
                    # 省平台
                    f'TIMEBEGIN_SHOW={self.startdate}&TIMEEND_SHOW={self.endtime}&TIMEBEGIN={self.startdate}&TIMEEND={self.endtime}&SOURCE_TYPE=1&DEAL_TIME=06&DEAL_CLASSIFY=00&DEAL_STAGE=0000&DEAL_PROVINCE=0&DEAL_CITY=0&DEAL_PLATFORM=0&BID_PLATFORM=0&DEAL_TRADE=0&isShowAll=1&PAGENUMBER={page}&FINDTXT=',
                    # 央企招投标
                    f'TIMEBEGIN_SHOW={self.startdate}&TIMEEND_SHOW={self.endtime}&TIMEBEGIN={self.startdate}&TIMEEND={self.endtime}&SOURCE_TYPE=2&DEAL_TIME=06&DEAL_CLASSIFY=01&DEAL_STAGE=0100&DEAL_PROVINCE=0&DEAL_CITY=0&DEAL_PLATFORM=0&BID_PLATFORM=0&DEAL_TRADE=0&isShowAll=1&PAGENUMBER={page}&FINDTXT='
                ]
                url = 'http://deal.ggzy.gov.cn/ds/deal/dealList_find.jsp'
                headers = {
                    'Content-Type': 'applasdaication/x-www-form-urlencoded; charset=UTF-8',
                    'user-agent': get_ua(),
                }
                if self.condition is True:
                    yield scrapy.Request(url=url, headers=headers, body=datas[i], method='POST', callback=self.lparse, meta={'data': datas[i]})
                else:
                    break

    def lparse(self, response):
        # conn = redis_conn()
        get_json = response.json().get('data', None)
        if get_json is None:
            msg = {
                'status': response.status,
                'url': response.meta['data'],
                'content': response.text
            }
            logger = self.logg()
            logger.info(json.dumps(obj=msg, ensure_ascii=False))
        else:
            for obj in get_json:
                classifyShow = obj.get('classifyShow', None)
                url = obj.get('url', None)
                timeShow = obj.get('timeShow', None)
                title = obj.get('title', None)

                curl = url.replace('html/a', 'html/b')
                meta = {
                    'title': title,
                    'timeShow': timeShow,
                    'classifyShow': classifyShow,
                }
                # result = conn.find_data(value=curl)
                # if result is False:
                yield scrapy.Request(url=curl, meta=meta, callback=self.cparse)
                # else:
                #     print('已存在:', curl)
                #     self.condition = False

    def cparse(self, response):
        item = {}
        content_result = process_content_type(C=response.text)
        item['docsubtitle'] = response.meta['title']
        item['publishdate'] = response.meta['timeShow']
        item['pagesource'] = response.text
        item['contenttype'] = content_result
        item['host'] = self.host
        item['type'] = self.type_id.get(response.meta['classifyShow'], '')

        # yield item
        print(item)

    def logg(self):
        os.makedirs('./loging', exist_ok=True)
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("./loging/log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
