from data_process import *
from redis_conn import *
from pymysql_connection import *
from fake_useragent import UserAgent
import requests


class CbircSpider:
    host = 'www.cbirc.gov.cn'
    name = 'cbirc'
    duplicates = True
    def start_requests(self):
        pages = [96, 1]

        for i in range(2):
            self.duplicates = True
            for page in range(1, pages[i] + 1):
                print(page)
                if page < 4:
                    urls = [
                        # 规章及规范性文件
                        f'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectDocByItemIdAndChild/data_itemId=928,pageIndex={page},pageSize=18.json',
                        # 法律法规
                        'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectDocByItemIdAndChild/data_itemId=927,pageIndex=1,pageSize=18.json'
                    ]
                else:
                    urls = [
                        # 规章及规范性文件
                        f'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocByItemIdAndChild?itemId=928&pageSize=18&pageIndex={page}',
                        # 法律法规
                        'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectDocByItemIdAndChild/data_itemId=927,pageIndex=1,pageSize=18.json'
                    ]

                url = urls[i]
                if self.duplicates is True:
                    try:
                        response = requests.get(url, proxies={'http': 'http://tps163.kdlapi.com:15818'})
                        response.encoding = 'utf-8'
                        self.lparse(response)
                    except:
                        print('重试')
                        response = requests.get(url, proxies={'http': 'http://tps163.kdlapi.com:15818'})
                        response.encoding = 'utf-8'
                        self.lparse(response)
                else:
                    break
                    # pass

    def lparse(self, response):
        jsult = response.json()['data']['rows']

        conn = redis_conn()
        for query in jsult:
            url = 'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectByDocId/data_docId=%s.json' %str(query['docId'])
            result = conn.find_data(field='政策库:', value=url)
            if result is False:
                response = requests.get(url)
                self.cparse(response)
                time.sleep(0.5)
            else:
                self.duplicates = False
                print('已存在', url)


    def cparse(self, response):
        try:
            jsult = response.json()
            item = {}
            data = jsult.get('data', '')
            docClob = data.get('docClob', '')
            document_number = data.get('documentNo', '')
            if document_number is None:
                document_number = ''
            docSubtitle = data.get('docSubtitle', '')
            publishDate = data.get('publishDate', None)
            cont = Xpath(docClob)
            cont = cont.xpath('', filter='style|script')
            if cont is None:
                attachmentInfoVOList = data.get('attachmentInfoVOList', None)[0]
                filename = attachmentInfoVOList.get('title', None)
                filelink = "https://www.cbirc.gov.cn" + attachmentInfoVOList.get('urlOtherName', None)
            else:
                filename = None
                filelink = None

            contenttype = process_content_type(C=cont, F=filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            item['contenttype'] = contenttype
            item['pageurl'] = response.url
            item['document_number'] = document_number
            item['docsubtitle'] = docSubtitle
            item['pub_date'] = publishDate
            item['doc_content'] = docClob
            item['source'] = 0

            print(item)
            ##########################
            # db = pymysql_connection()
            # db.insert_into_doc(fields=item)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    C = CbircSpider()
    C.start_requests()
