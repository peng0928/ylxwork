import scrapy
from data_process import *
from pymysql_connection import *
from redis_conn import *
from urllib.parse import urljoin
from lxml import etree


class SpiderSpider:
    name = 'pbcspider'
    start_urls = [
        # 行政法规
        'http://www.pbc.gov.cn/tiaofasi/144941/144953/index.html',
        # 规范性文件
        'http://www.pbc.gov.cn/tiaofasi/144941/3581332/3b3662a6/index1.html',
        # 部门规章
        'http://www.pbc.gov.cn/tiaofasi/144941/144957/21892/index1.html',

    ]
    start_pages = [1, 23, 6]
    duplicates = True
    def start_requests(self):
        for i in range(3):
            self.duplicates = True
            for page in range(1, self.start_pages[i]+1):
                print(i, page)
                if 'index1' in self.start_urls[i]:
                    url = self.start_urls[i].replace('index1', f'index{page}')
                else:
                    url = self.start_urls[i]

                if self.duplicates is True:
                    response = requests.post(url)
                    response.encoding = 'utf-8'
                    response = etree.HTML(response.text)
                    self.lparse(response)
                else:
                    break
                # pass

    def lparse(self, response):
        href = response.xpath("//font[@class='newslist_style']/a/@href")
        conn = redis_conn()
        for url in href:
            curl = 'http://www.pbc.gov.cn' + url

            if '.docx' not in curl:
                result = conn.find_data(field='政策库:', value=curl)
                if result is False:
                    response = requests.post(curl)
                    response.encoding = 'utf-8'
                    self.cparse(response)
                    time.sleep(1)
                else:
                    self.duplicates = False
                    print('已存在', curl)

    def cparse(self, response):
        try:
            result = Xpath(response.text)
            item = {}
            title = result.xpath("//h2")
            content = result.xpath("//td[@class='content']/div[@id='zoom']", filter='style|script')

            date = result.dpath("//span[@id='shijian']")

            file = result.fxpath("//div[@id='zoom']/p/a", rule="http://www.pbc.gov.cn")
            filename = file[0]
            filelink = file[1]

            contenttype = process_content_type(C=content, F=filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            item['contenttype'] = contenttype
            item['pageurl'] = response.url
            item['document_number'] = ''
            item['docsubtitle'] = title
            item['pub_date'] = date
            item['doc_content'] = content
            item['source'] = 3

            db = pymysql_connection()
            db.insert_into_doc(fields=item)
            # print(item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    C = SpiderSpider()
    C.start_requests()