# 网站链接 http://www.qhggzyjy.gov.cn/ggzy/
import scrapy, pymysql, time
from www_qhggzyjy_gov_cn.redis_conn import redis_conn
from www_qhggzyjy_gov_cn.data_process import *
from www_qhggzyjy_gov_cn.items import Item
from www_qhggzyjy_gov_cn.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.qhggzyjy.gov.cn'
    redis_name = '政府招标:' + host
    custom_settings = {
    'ITEM_PIPELINES': {
        f'{BOT_NAME}.pipelines.Pipeline': 300,
        # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
    },
    'LOG_LEVEL': 'INFO',

    # 允许状态码
    # 'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
    # 'COOKIES_ENABLED': False,
    # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
    # 'CONCURRENT_REQUESTS_PER_IP': 16
    # 'DOWNLOAD_DELAY': 0.6
    # 'CONCURRENT_REQUESTS': 32
}


    ############读取redis数据库爬取############
    def start_requests(self):
        conn = redis_conn()
        result = conn.get_data(field=redis_name)  # '政府招标:
        for query in result:
            data = str(query, encoding='utf-8').split('|')
            url = data[0]
            date = data[1]
            title = data[2]
            yield scrapy.Request(url=url, callback=self.cparse, meta={'date': date, 'title': title})
            # print(url, date, title)

    def cparse(self, res):
        item = Item()
        try:
            result = Xpath(res.text)
            title = res.meta['title']
            date = res.meta['date']
            content = result.xpath("//div[@class='info xiangxiyekuang']|//div[@class='ewb-info-content']", filter="a[@class='want-btn']|script|div[@id='att']")
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


    # def start_requests(self):
    #     headers = {
    #         'Host': 'www.qhggzyjy.gov.cn',
    #         'Origin': 'http://www.qhggzyjy.gov.cn',
    #         'Referer': 'http://www.qhggzyjy.gov.cn/ggzy/jyxx/001002/001002005/transinfo_list.html',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    #         'X-Requested-With': 'XMLHttpRequest',
    #     }
    #     for i in range(4):
    #         num = 0
    #         for page in range(100):
    #             url = 'http://www.qhggzyjy.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData'
    #             data = [
    #                 # 采购公告
    #                 '{"token":"","pn":%d,"rn":10,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001;002;003;004;005;006;007;008;009;010","sort":"{\\"showdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"001002001"}],"time":null,"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"100","noParticiple":"0","searchRange":null,"isBusiness":1}'%num,
    #                 # 澄清变更
    #                 '{"token":"","pn":%d,"rn":10,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001;002;003;004;005;006;007;008;009;010","sort":"{\\"showdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"001002002"}],"time":null,"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"100","noParticiple":"0","searchRange":null,"isBusiness":1}'%num,
    #                 # 中标公示
    #                 '{"token":"","pn":%d,"rn":10,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001;002;003;004;005;006;007;008;009;010","sort":"{\\"showdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"001002004"}],"time":null,"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"100","noParticiple":"0","searchRange":null,"isBusiness":1}'%num,
    #                 # 终止公告
    #                 '{"token":"","pn":%d,"rn":10,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"title","cnum":"001;002;003;004;005;006;007;008;009;010","sort":"{\\"showdate\\":\\"0\\"}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","isLike":true,"likeType":2,"equal":"001002005"}],"time":null,"highlights":"title","statistics":null,"unionCondition":null,"accuracy":"100","noParticiple":"0","searchRange":null,"isBusiness":1}'%num,
    #             ]
    #             num += 10
    #             print(i ,page)
    #             yield scrapy.Request(url=url, method='POST', body=data[i],
    #                                  callback=self.dparse)
    # # 链接|时间|标题
    # def dparse(self, res):
    #     try:
    #         r = redis_conn()
    #         query = res.json()['result']['records']
    #         for data in query:
    #             item = 'https://www.qhggzyjy.gov.cn' + data['linkurl'] + '|' + data['infodate'] + '|' + data['title']
    #             r.set_add(redis_name, item)
    #             # print(item)
    #
    #     except Exception as e:
    #         print(e)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
