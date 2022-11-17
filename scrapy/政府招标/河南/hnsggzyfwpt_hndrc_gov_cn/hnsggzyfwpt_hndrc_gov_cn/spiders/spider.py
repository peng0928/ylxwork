import scrapy, json
from hnsggzyfwpt_hndrc_gov_cn.items import ddItem
from hnsggzyfwpt_hndrc_gov_cn.pymysql_connection import pymysql_connection
from hnsggzyfwpt_hndrc_gov_cn.data_process import *
from hnsggzyfwpt_hndrc_gov_cn.redis_conn import *
from hnsggzyfwpt_hndrc_gov_cn.items import Item


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'hnsggzyfwpt.hndrc.gov.cn'

    def start_requests(self):
        condition = True
        for page in range(1, 351):
            page = str(page)
            url = f'http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex={page}&pageSize=22&day=89&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002002001&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38'

            res = get_link_json(url)
            res = res['return']
            res_json = json.loads(res)
            table = res_json['Table']
            for query in table:
                url = 'http://hnsggzyfwpt.hndrc.gov.cn' + query['href']
                conn = redis_conn()
                result = conn.find_data(value=url)
                if result is False:
                    yield scrapy.Request(url=url, callback=self.con_parse)
                else:
                    condition = False
            if condition is False:
                break
                # pass
            # yield scrapy.Request(url=url, callback=self.dparse)

    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h1[@class='ewb-left-tt']")
            date = result.dpath("//div[@class='ewb-left-info']", rule=None)
            content = result.xpath("//div[@class='ewb-left-bd']", filter="div[@class='ewb-left-art']|script|style")
            filename = response.xpath(
                "//div[@class='ewb-left-bd']//td/a/text()|//div[@class='con']/span/a/text()").getall() or None
            filelink = response.xpath(
                "//div[@class='ewb-left-bd']//td/a/@href|//div[@class='con']/span/a/@href").getall() or None
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
            print(item)
            # yield item

        except Exception as e:
            print(e)


# 启动
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
