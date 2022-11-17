from data_process import *
from redis_conn import *
from pymysql_connection import *


class SpiderSpider:
    name = 'spider'
    start_urls = [
        'http://www.csrc.gov.cn/searchList/cd11df89f5894c1eac37ae37cc11e369?_isAgg=true&_isJson=true&_pageSize=10&_template=index&_rangeTimeGte=&_channelName=&page='
    ]
    duplicates = True
    def start_requests(self):
        for page in range(1, 21):
            if self.duplicates is True:
                response = requests.get(url=self.start_urls[0].replace('page=', f'page={page}'))
                response.encoding = 'utf-8'
                self.lparse(response)
            else:
                break

    def lparse(self, response):
        result = response.json()['data']['results']
        conn = redis_conn()
        for data in result:
            lurl = data['url']
            content = data['content']
            title = data['title']
            publishedTimeStr = data['publishedTimeStr']
            publishedTimeStr = process_date(publishedTimeStr)


            result = conn.find_data(field='政策库:', value=lurl)
            if result is False:
                response = requests.get(lurl)
                response.encoding = 'utf-8'
                self.cparse(response, meta={'content': content, 'title': title, 'publishedTimeStr': publishedTimeStr})
                time.sleep(1)
            else:
                self.duplicates = False
                print('已存在', lurl)

    def cparse(self, response, meta=None):
        try:
            title = meta['title']
            pudate = meta['publishedTimeStr']
            content = meta['content']
            content = replace(content)
            result = Xpath(response.text)
            item = {}
            document_number = result.xpath("//div[@class='xxgk-table']/table/tbody/tr[4]/td[1]")
            file = result.fxpath("//div[@id='files']/a", rule="http://www.csrc.gov.cn")
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
            item['source'] = 2
            # print(item)

            db = pymysql_connection()
            db.insert_into_doc(fields=item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    C = SpiderSpider()
    C.start_requests()