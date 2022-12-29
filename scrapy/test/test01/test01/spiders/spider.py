import scrapy

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    start_urls = ['https://www.runoob.com/']

    def __init__(self, *args, **kwargs):
        super(SpiderSpider, self).__init__(*args, **kwargs)
        self.pname = []
        self.listing_url = (kwargs.get('listing_url'))
        self.listing_name = (kwargs.get('listing_name'))
        self.listing_value = (kwargs.get('listing_value'))

        print(kwargs)

    def start_requests(self):
        print(self.start_urls)
        yield scrapy.Request(url=self.start_urls[0], callback=self.lparse)

    def lparse(self, response):
        print(response.text)