import scrapy
from www_pbc_gov_cn.data_process import *
from urllib.parse import urljoin

class SpiderSpider(scrapy.Spider):
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
    def start_requests(self):
        for i in range(3):
            for page in range(1, self.start_pages[i]+1):
                if 'index1' in self.start_urls[i]:
                    url = self.start_urls[i].replace('index1', f'index{page}')
                else:
                    url = self.start_urls[i]

                yield scrapy.Request(url=url, method='POST', callback=self.lparse)

    def lparse(self, response):
        href = response.xpath("//font[@class='newslist_style']/a/@href").getall()
        for url in href:
            curl = 'http://www.pbc.gov.cn' + url
            print(response.url)
            yield scrapy.Request(url=curl, method='POST', callback=self.cparse)

    def cparse(self, response):
        print(response.url)
        result = Xpath(response.text)
        item = {}
        title = result.xpath("//h2")
        content = result.xpath("//div[@id='zoom']/div|//div[@id='zoom']//a/@href", filter='style|script')
        # if '.pdf' in content:
        #     contents = content.split('\n')
        #     content = ''
        #     for i in contents:
        #         content += urljoin('http://www.pbc.gov.cn', i) + '\n'
        #     print(content)
        date = result.dpath("//span[@id='shijian']")

        item['title'] = title
        item['content'] = content
        item['date'] = date
        print(item)

############## 启动 ##############
if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(f'scrapy crawl {SpiderSpider.name}'.split())