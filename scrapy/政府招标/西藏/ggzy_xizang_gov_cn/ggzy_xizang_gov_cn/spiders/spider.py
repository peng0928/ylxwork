# http://ggzy.xizang.gov.cn/
import scrapy, pymysql, time, requests, json
from ggzy_xizang_gov_cn.redis_conn import redis_conn
from ggzy_xizang_gov_cn.data_process import *
from ggzy_xizang_gov_cn.items import Item
from ggzy_xizang_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzy.xizang.gov.cn'

    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3
        # 'CONCURRENT_REQUESTS': 32
    }

    def start_requests(self):
        for page in range(2163):
            condition = True
            url = f'https://ggzy.xizang.gov.cn/jyxxzc_{page}.jhtml'
            query = get_link(url=url, rpath="//div[@class='detail_content_right_box_content']//p/@onclick")
            for item in query:
                item = re.findall("'(.*?)'", item)[0]
                lurl = 'https://ggzy.xizang.gov.cn' + item

                conn = redis_conn()
                result = conn.find_data(value=lurl)
                if result is False:
                    yield scrapy.Request(url=lurl, callback=self.con_parse)
                else:
                    print('已存在:', lurl)
                    condition = False
            if condition is False:
                break

    def con_parse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            projectCode = result.xpath("//div[@class='title-code']").split('：')[-1]
            headers = {'Content-Type': 'application/json', }
            data = {"projectCode": f"{projectCode}", "path": f"{res.url.split('/')[-2]}", "sId": 22}
            data = json.dumps(data)
            resp = requests.post(headers=headers, url='https://ggzy.xizang.gov.cn/personalitySearch/initDetailbyProjectCode', data=data)
            resp.encoding = 'utf-8'
            res_txt = json.loads(resp.text)['data']['listData'][0]
            content = res_txt['txt']
            date = res_txt['publishTime']
            title = res_txt['title']
            res_result = Xpath(content)
            content = res_result.xpath("", filter='script|style|title')
            content_result = process_content_type(C=content)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = date
            item['contenttype'] = content_result
            item['doc_content'] = content
            yield item
            # print(item)

        except Exception as e:
            print(e, res.url)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
