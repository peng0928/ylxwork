import scrapy, json
from www_ccgp_guizhou_gov_cn.data_process import *
from www_ccgp_guizhou_gov_cn.redis_conn import redis_conn
from www_ccgp_guizhou_gov_cn.items import Item

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    redis_name = '政府招标:www.ccgp-guizhou.gov.cn'
    host = 'www.ccgp-guizhou.gov.cn'
    headers = {
        'Cookie': '_zcy_log_client_uuid=992d4d00-0e0d-11ed-b603-7737766d8fb4',
        'Host': 'www.ccgp-guizhou.gov.cn',
        'Origin': 'http://www.ccgp-guizhou.gov.cn',
        'Referer': 'http://www.ccgp-guizhou.gov.cn/ZcyAnnouncement/ZcyAnnouncement1/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    def start_requests(self):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        start_url = 'http://www.ccgp-guizhou.gov.cn/front/search/category'
        start_index = [10016, 3014, 3012, 33, 3001, 333, 3005, 3004, 3015, 3017, 3010]
        for i in range(11):
            condition = True
            for page in range(1,661):
                data = '{"categoryCode":"ZcyAnnouncement%s","pageSize":"15","pageNo":"%s"}' % (start_index[i], page)
                hits = post_link_json(url=start_url, data=data, headers=headers)['hits']['hits']
                for query in hits:
                    lurl = 'http://www.ccgp-guizhou.gov.cn' + query['_source']['url']
                    conn = redis_conn()
                    result = conn.find_data(value=lurl)
                    if result is False:
                        yield scrapy.Request(url=lurl, headers=headers, callback=self.con_parse)
                    else:
                        print('已存在:', lurl)
                        condition = False
                if condition is False:
                    break

    def con_parse(self, res):
        item = Item()
        try:
            data = res.xpath("//input/@value").extract()
            data = json.loads(data[1])
            title = data['title']
            publishDate = data['publishDate']

            content = data['content']
            content = Xpath(content, )
            content = content.xpath("", filter='style|script')

            content = process_text(content)
            date = process_date(data=publishDate)
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
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
