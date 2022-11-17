from data_process import *
from redis_conn import *
from pymysql_connection import *


class SpiderSpider:
    name = 'spider'
    start_urls = [
        'https://www.china-cba.net/Index/lists/catid/16/p/1.html',
        'https://www.china-cba.net/Index/lists/catid/16/p/2.html',
        'https://www.china-cba.net/Index/lists/catid/16/p/3.html',
    ]
    duplicates = True
    def start_requests(self):
        for url in self.start_urls:
            if self.duplicates is True:
                response = requests.get(url)
                response.encoding = 'utf-8'
                response = etree.HTML(response.text)
                self.lparse(response)
            else:
                break

    def lparse(self, response):
        result = response.xpath("//div[@class='q3_r fix']/ul/li/a/@href")
        conn = redis_conn()
        for urls in result:
            lurl = 'https://www.china-cba.net' + urls

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
            title = result.xpath("//div[@class='d6_tit fix']/h3")
            pudate = result.dpath("//div[@class='d6_d1 fix']")
            content = result.xpath("//div[@id='neirong']")

            file = result.fxpath("//div[@id='neirong']//a", rule="https://www.china-cba.net")
            filename = file[0]
            filelink = file[1]

            contenttype = process_content_type(C=content, F=filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            item['contenttype'] = contenttype
            item['pageurl'] = response.url
            item['document_number'] = ''
            item['docsubtitle'] = title
            item['pub_date'] = pudate
            item['doc_content'] = content
            item['source'] = 1

            db = pymysql_connection()
            db.insert_into_doc(fields=item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    C = SpiderSpider()
    C.start_requests()