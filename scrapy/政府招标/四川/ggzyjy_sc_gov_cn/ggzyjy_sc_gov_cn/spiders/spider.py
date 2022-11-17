import scrapy, json
from ggzyjy_sc_gov_cn.redis_conn import redis_conn
from ggzyjy_sc_gov_cn.data_process import *
from ggzyjy_sc_gov_cn.items import Item
from ggzyjy_sc_gov_cn.useragent import get_ua

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'ggzyjy.sc.gov.cn'
    redis_name = '政府招标:四川:ggzyjy.sc.gov.cn'
    # redis断点
    # 采集时间范围 startTime 2020-01-01 endTime 2022-8-2
    start_urls = ['http://ggzyjy.sc.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData']

    headers = {
                'Cookie': 'userGuid=-2001935666',
                'Host': 'ggzyjy.sc.gov.cn',
                'User-Agent': get_ua(),
                'X-Requested-With': 'XMLHttpRequest',}

    def start_requests(self):
        for page in range(1, 1000):
            condition = True
            pn = page * 12
            data = '''{"token":"","pn":%d,"rn":12,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"","sort":"{'webdate':'0'}","ssort":"title","cl":500,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002002","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":[{"fieldName":"webdate","startTime":"2022-7-11 00:00:00","endTime":"2022-8-11 23:59:59"}],"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"0","searchRange":null,"isBusiness":"1"}'''%(pn)
            query = post_link_json(url=self.start_urls[0], data=data)
            result = query['result']['records']
            for query in result:
                linkurl = 'http://ggzyjy.sc.gov.cn' + query['linkurl']

                conn = redis_conn()
                result = conn.find_data(value=linkurl)
                if result is False:
                    yield scrapy.Request(url=linkurl, headers=self.headers, callback=self.con_parse)
                else:
                    print('已存在:', linkurl)
                    condition = False
            if condition is False:
                break
                # pass


    def con_parse(self, response):
        item = Item()
        try:
            result = Xpath(response.text)
            title = result.xpath("//h2[@class='detailed-title']")
            date = result.dpath("//span[@id='date']|//div[@class='tab-view-son']/div[2]//p[@class='detailed-desc']", rule='发布时间：')
            content = result.xpath("//div[@id='newsText']|//div[@id='noticeArea']", filter='style|h2')

            # file = result.fxpath("//div[@id='newsText']|//div[@id='noticeArea']//a")
            # filename = file[0]
            # filelink = file[1]
            #
            # item['filename'] = filename
            # item['filelink'] = filelink
            content_result = process_content_type(C=content, F=None)
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


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
