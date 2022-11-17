from data_process import *
from pymysql_connection import *


class SpiderSpider:
    name = 'safespider'
    start_urls = ['https://www.safe.gov.cn/safe/zcfg/index.html']
    duplicates = True
    def start_requests(self):
        for page in range(1, 28):
            print(page)
            self.duplicates = True
            if page > 1:
                url = self.start_urls[0].replace('index', f'index_{page}')
            else:
                url = self.start_urls[0]

            if self.duplicates is True:
                response = requests.get(url)
                response.encoding = 'utf-8'
                response = etree.HTML(response.text)
                self.lparse(response)
            else:
                break

    def lparse(self, response):
        result = response.xpath("//div[@class='list_conr']/ul/li/dt/a/@href")
        conn = redis_conn()
        for url in result:
            lurl = 'https://www.safe.gov.cn' + url

            result = conn.find_data(field='政策库:', value=lurl)
            if result is False:
                response = requests.get(lurl)
                response.encoding = 'utf-8'
                self.cparse(response)
                time.sleep(1)
            else:
                self.duplicates = False
                print('已存在', lurl)

    def cparse(self, response):
        try:
            result = Xpath(response.text)
            item = {}
            title = result.xpath("//div[@class='detail_tit']")
            pudate = result.xpath("//div[@class='condition']/ul/li[4]/dd")
            document_number = result.xpath("//span[@id='wh']")
            if document_number is None:
                document_number = ''
            content = result.xpath("//div[@id='content']")

            file = result.fxpath("//div[@id='content']//p//a", rule="https://www.safe.gov.cn")
            filename = file[0]
            filelink = file[1]

            contenttype = process_content_type(C=content, F=filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            item['contenttype'] = contenttype
            item['pageurl'] = response.url
            item['document_number'] = document_number
            item['docsubtitle'] = title
            item['pub_date'] = pudate
            item['doc_content'] = content
            item['source'] = 4

            db = pymysql_connection()
            db.insert_into_doc(fields=item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    C = SpiderSpider()
    C.start_requests()
