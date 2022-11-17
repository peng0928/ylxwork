import scrapy, requests, rsa
from ..data_process import *
from ..redis_conn import *


class JiLinSpider(scrapy.Spider):
    name = 'spider'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "_gscu_1208125908=66171183wvjgob29; _gscbrs_1208125908=1; _gscs_1208125908=t66228251joxb6c14|pv:34",
        "Host": "www.ccgp-jilin.gov.cn",
        "Origin": "http://www.ccgp-jilin.gov.cn",
        "Referer": "http://www.ccgp-jilin.gov.cn/ext/search/morePolicyNews.action",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }
    host = 'www.ccgp-jilin.gov.cn'
    condition = True
    def start_requests(self):
        ss = self.get_ss(Change=True)
        urls = ['http://www.ccgp-jilin.gov.cn/ext/search/morePolicyNews.action']
        pages = [140, 1500, 6, 300, 600, 100, 400, 4000, 1000, 1500, 3000, 30, 700, 2, 300, 100, 30, 25, 1000, 150, 400, 500]
        datas = [
            # 市县采购公告
            f'currentPage=&noticetypeId=1&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 资格预审
            f'currentPage=&noticetypeId=2&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 公开招标
            f'currentPage=&noticetypeId=7&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 邀请招标
            f'currentPage=&noticetypeId=4&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 竞争性谈判
            f'currentPage=&noticetypeId=5&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 竞争性磋商
            f'currentPage=&noticetypeId=6&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 单一来源
            f'currentPage=&noticetypeId=3&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 询价公告
            f'currentPage=&noticetypeId=9&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 中标公告
            f'currentPage=&noticetypeId=10&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 成交公告
            f'currentPage=&noticetypeId=11,12,8&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',# 废标、更正、其他公告
            f'currentPage=&noticetypeId=13,14&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 合同、验收公告

            # 省级采购公告
            f'currentPage=&noticetypeId=1&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 资格预审
            f'currentPage=&noticetypeId=2&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 公开招标
            f'currentPage=&noticetypeId=7&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 邀请招标
            f'currentPage=&noticetypeId=4&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 竞争性谈判
            f'currentPage=&noticetypeId=5&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 竞争性磋商
            f'currentPage=&noticetypeId=6&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 单一来源
            f'currentPage=&noticetypeId=3&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 询价公告
            f'currentPage=&noticetypeId=9&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 中标公告
            f'currentPage=&noticetypeId=10&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 成交公告
            f'currentPage=&noticetypeId=11,12,8&categoryId=124&articleId=1&ss={ss}&id=1&pager.pageNumber=1',
            # 废标、更正、其他公告
            f'currentPage=&noticetypeId=13,14&categoryId=125&articleId=1&ss={ss}&id=1&pager.pageNumber=1',  # 合同、验收公告

        ]
        for i in range(len(datas)):
            for page in range(pages[i]):
                if self.condition is True:
                    body = datas[i].replace('currentPage=', f'currentPage={page}')
                    yield scrapy.Request(url=urls[0], body=body, headers=self.headers, method='POST', callback=self.lparse, meta={'data': body, 'retry_times': 0})
                else:
                    break

    def lparse(self, response):
        conn = redis_conn()
        lresult = response.xpath("//div[@id='list_right']/ul/li/a/@href").getall()

        lurls = url_join(response.url, lresult)
        for lurl in lurls:
            result = conn.find_data(value=lurl)
            if result is False:
                yield scrapy.Request(url=lurl, headers=self.headers, callback=self.cparse)
            else:
                print('已存在:', lurl)
                self.condition = False

    def cparse(self, response):
        item = {}
        title = response.xpath("//h2[@class='sd']//text()").get()
        data_res = Xpath(response.text)
        pudate = data_res.dpath("//h3[@class='wzxq']")

        content = response.text
        content_result = process_content_type(C=content)
        item['host'] = self.host
        item['pageurl'] = response.url
        item['publishdate'] = pudate
        item['docsubtitle'] = title
        item['pagesource'] = content
        item['contenttype'] = content_result
        print(item)
        # yield item

    def get_ss(self, Change=False):
        if Change:
            resp = post_link_json(url='http://www.ccgp-jilin.gov.cn/ext/search/ext/search/keyPair.action')
            keyId = resp['keyId']
            exponent = resp['map']['exponent']
            modulus = resp['map']['modulus']
            en = Encrypt(exponent, modulus)
            with open('./ss.txt', 'w')as f:
                f.write(en.encrypt(keyId))

        with open('./ss.txt', 'r')as f:
            r = f.read()
        return r


class Encrypt(object):
    def __init__(self, e, m):
        self.e = e
        self.m = m

    def encrypt(self, message):
        mm = int(self.m, 16)
        ee = int(self.e, 16)
        rsa_pubkey = rsa.PublicKey(mm, ee)
        crypto = self._encrypt(message.encode(), rsa_pubkey)
        return crypto.hex()

    def _pad_for_encryption(self, message, target_length):
        message = message[::-1]
        max_msglength = target_length - 11
        msglength = len(message)

        padding = b''
        padding_length = target_length - msglength - 3

        for i in range(padding_length):
            padding += b'\x00'

        return b''.join([b'\x00\x00', padding, b'\x00', message])

    def _encrypt(self, message, pub_key):
        keylength = rsa.common.byte_size(pub_key.n)
        padded = self._pad_for_encryption(message, keylength)

        payload = rsa.transform.bytes2int(padded)
        encrypted = rsa.core.encrypt_int(payload, pub_key.e, pub_key.n)
        block = rsa.transform.int2bytes(encrypted, keylength)

        return block