import scrapy


class DemoSpider(scrapy.Spider):
    name = 'demo'
    start_url = ['']
    url = 'http://www.hizj.net:8008/WebSite_Publish/Default.aspx?action=IntegrityMge/ucCreditCompanyInfoList&Type=工程监理企业资质'
    h = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "ASP.NET_SessionId=nmmio345azryo5551aigiuv2; ASP.NET_SessionId_NS_Sig=oenCV6mdx2N9-BO4",
        "Host": "www.hizj.net:8008",
        "Origin": "http://www.hizj.net:8008",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }

    def start_requests(self):
        yield scrapy.Request(method='POST', url=self.url, headers=self.h, callback=self.lparse)

    def lparse(self, response):
        ListItem_Left = response.xpath("//td[@class='ListItem_Left']/a/text()").getall()
        print(ListItem_Left)
        for pagenow in range(1, 11):
            data = f'__EVENTTARGET=ID_IntegrityMge_ucCreditCompanyInfoList%24ucPager1%24btnNext&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPBS5WaWV3U3RhdGVfMWJjMWY0M2MtYTJkNi00ZTA0LWI0YjMtZWY4NmJkODA1NTIwGAEFMElEX0ludGVncml0eU1nZV91Y0NyZWRpdENvbXBhbnlJbmZvTGlzdCRncmlkVmlldw8UKwAKZGRkZGRkFQEER3VpZBQrAA8UKwABBSRlM2VkOTllMC1lYTIwLTQ5ZDAtOGVhOS1lNTc1OTNmNTMzN2UUKwABBSQ3NGI3ZmNiNC0xMjU1LTRiYjQtOTY0Yi03NmU4NzYwZmUwZmQUKwABBSRmNzgzZThkZi1jOGQxLTRlNGQtYWI0Ny1iMjY5YzI2MTNiMTIUKwABBSQ3YmVlYjY0Zi1hNDk1LTRkODItYjE1Zi01NDU5Y2UyNTZiYTMUKwABBSQzNTNlYzk4NC03OTE0LTRlYzgtYWIwOC01NmYyYTM4NGYzYzYUKwABBSQxNjg3N2Y5Mi03YjNlLTQwODItOGFlYy0xMTk5N2ZkMWI3MmQUKwABBSRmNDM2MTdiZi0xYTY1LTQ4ZDctOTAwNS03YmM3MzYwMTkwYWEUKwABBSQwNjlmMmYyMS00YjUzLTRkYzAtYTdkZC02MGM3YjhlNDg3Y2QUKwABBSQwYzgwMTFmMS05ODNhLTQxMTYtOGUzZi03ODE1ZDg0N2M4NTUUKwABBSQ2NmFiZjhjYi0zY2YwLTQ0ZmUtOWQ5Ni04NWM0NGFkNzNmY2EUKwABBSQyZTdmMjEyOS1jNGQ2LTQ2ODMtOWNkMy03ODljZTQzMGQ3NDQUKwABBSQ3NjQxNmNkZC1lNWI1LTQ5ZWQtYTMwNS1jMmVkZjAzYTU5YjYUKwABBSRkZDBkNjYyNi1jZGUxLTRhNzgtODgyYi01ODhlMmFlYjk5M2MUKwABBSRmMzRiMjM5NC0yMmIzLTQyZTQtYmI0My00MjEwMDYyMGVmMzgUKwABBSQ1NjkwMzEyYy1iMmM3LTQ0ZDItOGY1OS0wZWM2NmQ4NGNiNWECARQrAAEFJGUzZWQ5OWUwLWVhMjAtNDlkMC04ZWE5LWU1NzU5M2Y1MzM3ZWSQ4JrrjqeKoQDgFyFnZaHbi5VaZQ%3D%3D&__VIEWSTATEGENERATOR=F006C583&ID_IntegrityMge_ucCreditCompanyInfoList%24txtProjectName=&ID_IntegrityMge_ucCreditCompanyInfoList%24ddlProvince=%E5%85%A8%E9%83%A8&ID_IntegrityMge_ucCreditCompanyInfoList%24txtValidCode=&ID_IntegrityMge_ucCreditCompanyInfoList%24ucPager1%24txtCurrPage={pagenow}'
            yield scrapy.Request(method='POST', url=self.url, headers=self.h, body=data, callback=self.lparse2)

    def lparse2(self, response):
        ListItem_Left = response.xpath("//td[@class='ListItem_Left']/a/text()").getall()
        print(ListItem_Left)


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute('scrapy crawl demo'.split())
