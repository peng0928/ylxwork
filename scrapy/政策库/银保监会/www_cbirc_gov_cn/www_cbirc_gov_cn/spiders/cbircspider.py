import scrapy
from scrapy import cmdline
from www_szse_cn.data_process import *
from www_szse_cn.redis_conn import *
from fake_useragent import UserAgent

class CbircSpider(scrapy.Spider):
    host = 'www.cbirc.gov.cn'
    name = 'cbirc'
    duplicates = True

    def start_requests(self):
        pages = [15, 1]
        for i in range(2):
            for page in range(1, pages[i] + 1):
                urls = [
                    # 规章及规范性文件
                    f'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocByItemIdAndChild?itemId=928&pageSize=18&pageIndex={page}',
                    # 法律法规
                    'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectDocByItemIdAndChild/data_itemId=927,pageIndex=1,pageSize=18.json'
                ]
                url = urls[i]
                if self.duplicates is True:
                    yield scrapy.Request(url=url, callback=self.lparse)
                else:
                    break

    def lparse(self, response):
        jsult = response.json()['data']['rows']
        conn = redis_conn()
        for query in jsult:
            headers = {'User-Agent': UserAgent().random}
            url = 'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectByDocId/data_docId=%s.json' %str(query['docId'])
            # result = conn.find_data(value=url)
            # if result is False:
            yield scrapy.Request(url=url, headers=headers, callback=self.cparse)

            # else:
                # self.duplicates = False
                # print('已存在', url)


    def cparse(self, response):
        print(response.url, )
        jsult = response.json()
        data = jsult.get('data', None)
        documentNo = data.get('documentNo', None)
        docSubtitle = data.get('docSubtitle', None)
        publishDate = data.get('publishDate', None)
        # docClob = jsult.get('docClob', None)
        # cont = Xpath(docClob)
        # cont = cont.xpath('')
        print(documentNo, docSubtitle, publishDate)


if __name__ == '__main__':
    cmdline.execute(f'scrapy crawl {CbircSpider.name}'.split())
