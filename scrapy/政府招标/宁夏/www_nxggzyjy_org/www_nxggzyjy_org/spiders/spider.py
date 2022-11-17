# http://www.nxggzyjy.org/
import scrapy, pymysql, time, requests
from www_nxggzyjy_org.redis_conn import redis_conn
from www_nxggzyjy_org.data_process import *
from www_nxggzyjy_org.items import Item
from www_nxggzyjy_org.settings import *


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    host = 'www.nxggzyjy.org'
    custom_settings = {
        'ITEM_PIPELINES': {
            f'{BOT_NAME}.pipelines.Pipeline': 300,
            # 'crawlab.pipelines.CrawlabMongoPipeline': 888, # 5.0
        },
        'LOG_LEVEL': 'INFO',

        # 允许状态码
        'HTTPERROR_ALLOWED_CODES': [403, 404, 400],
        # 'COOKIES_ENABLED': False,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16
        # 'CONCURRENT_REQUESTS_PER_IP': 16
        'DOWNLOAD_DELAY': 3
        # 'CONCURRENT_REQUESTS': 32
    }

    def start_requests(self):
        for i in range(7):
            page = 0
            condition = True
            for p in range(500):
                start_datas = [
                    # 工程建设项目- 招标/资审公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002001001","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,
                    # 工程建设项目- 澄清/变更公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002001002","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,
                    # 工程建设项目- 中标候选人公示
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002001004","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,
                    # 工程建设项目- 中标公示/公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002001003","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,

                    # 政府采购项目- 采购公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002002001","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,
                    # 政府采购项目- 澄清/变更公告
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002002002","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,
                    # 政府采购项目- 中标/成交公示
                    '{"token":"","pn":%d,"rn":20,"sdt":"","edt":"","wd":"","inc_wd":"","exc_wd":"","fields":"","cnum":"","sort":"{\\"istop\\":\\"0\\",\\"ordernum\\":\\"0\\",\\"webdate\\":\\"0\\",\\"infoid\\":\\"0\\"}","ssort":"","cl":10000,"terminal":"","condition":[{"fieldName":"categorynum","equal":"002002003","notEqual":null,"equalList":null,"notEqualList":null,"isLike":true,"likeType":2}],"time":null,"highlights":"","statistics":null,"unionCondition":null,"accuracy":"","noParticiple":"1","searchRange":null,"noWd":true}' % page,
                ]
                page += 20
                url = 'http://www.nxggzyjy.org/inteligentsearch_es/rest/esinteligentsearch/getFullTextDataNew'
                data = start_datas[i]
                query = post_link_json(url, data=data)['result']['records']
                for data in query:
                    infoid = data['infoid']
                    url = f'https://www.nxggzyjy.org/ningxiawebservice/services/BulletinWebServer/getInfoDetail?response=application/json&siteguid=2e221293-d4a1-40ed-854b-dcfea12e61c5&infoid={infoid}'
                    resp = requests.get(url)
                    lurl = 'http://www.nxggzyjy.org/ningxiaweb' + resp.json()['return']
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
            title = result.xpath("//h3[@class='ewb-main-h2'][2]")
            date = result.dpath("//div[@class='ewb-main-bar']", rule=None)
            content = result.xpath("//div[@class='ewb-main']", filter="div[@id='applyId']|script|div[@class='ewb-main-bar']|div[@id='ewblevelid']|div[@id='ewblevelfont']|div[@class='ewb-tab-con-hd']|style|h3")
            content_result = process_content_type(C=content)

            item['host'] = self.host
            item['pageurl'] = res.url
            item['docsubtitle'] = title
            item['publishdate'] = date
            item['contenttype'] = content_result
            item['doc_content'] = content
            # yield item
            print(item)

        except Exception as e:
            print(e)


############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())
