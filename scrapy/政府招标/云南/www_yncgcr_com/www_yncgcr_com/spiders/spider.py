import scrapy
from www_yncgcr_com.redis_conn import redis_conn
from www_yncgcr_com.useragent import get_ua
from www_yncgcr_com.data_process import *
from www_yncgcr_com.items import Item

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    redis_name = '政府招标:www.yncgcr.com'
    host = 'www.yncgcr.com'
    start_urls = [
        'http://www.yncgcr.com/jyxx/zfcg/cggg',  # 招标（谈判、询价、更正）公告
        'http://www.yncgcr.com/jyxx/zfcg/zbjggs',  # 结果公示
    ]

    start_pages = [
        97, 67
    ]
    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.yncgcr.com',
            'Origin': 'http://www.yncgcr.com',
            'Referer': 'http://www.yncgcr.com/jyxx/zfcg/zbjggs',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        for i in range(2):
            condition = True
            for page in range(1, self.start_pages[i]):
                data = f'currentPage={page}'
                url = self.start_urls[i]

                query = post_link(url, "//td[@class='text_left']/a/@href", data=data, headers=headers)
                for item in query:
                    url = 'http://www.yncgcr.com' + item

                    conn = redis_conn()
                    result = conn.find_data(value=url)
                    if result is False:
                        yield scrapy.Request(url=url, callback=self.con_parse)
                    else:
                        condition = False
                if condition is False:
                    break
                    # pass

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h3[@class='detail_t']")
            date = result.dpath("//p[@class='kdg']", rule=None)
            content = result.xpath("//div[@class='detail_contect']", filter="script|style")

            filename = response.xpath("//div[@class='detail_contect']//td/a/text()").extract() or None
            filelink = response.xpath("//div[@class='detail_contect']//td/a/@href").extract() or None
            if filelink is not None and filename is not None:
                fileurl = ''
                filename = '|'.join(filename)
                filelink = fileurl + f'|{fileurl}'.join(filelink)
            item['filename'] = filename
            item['filelink'] = filelink
            content_result = process_content_type(C=content, F=filelink)
            item['host'] = self.host
            item['pageurl'] = response.url
            item['publishdate'] = date
            item['docsubtitle'] = title
            item['doc_content'] = content
            item['contenttype'] = content_result
            # print(item)
            yield item

        except Exception as e:
            print(e)



############# 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
