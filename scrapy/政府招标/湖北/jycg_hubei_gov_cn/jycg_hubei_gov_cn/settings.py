# Scrapy settings for jycg_hubei_gov_cn project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'jycg_hubei_gov_cn'

SPIDER_MODULES = ['jycg_hubei_gov_cn.spiders']
NEWSPIDER_MODULE = 'jycg_hubei_gov_cn.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jycg_hubei_gov_cn (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1.5
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
LOG_LEVEL = 'INFO'
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False
HTTPERROR_ALLOWED_CODES = [403,404,400, 412]
# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#   'Cookie': 'JSESSIONID=72A880C55FA6138FB1BBB173E03F8AEE; _trs_uv=l64b38co_4085_1nzs; _trs_gv=g_l64b38co_4085_1nzs; FSSBBIl1UgzbN7N80S=fofl7v2WB2urKptQyaPEJd2AgrHBGeOqv4L7GZO.3obF0QYjjRimlKz04zu5J.2s; dataHide2=c75dea02-b29c-4acc-bc7c-4c19962d7b2c; Hm_lvt_197b0a423d2d21ba532734d13a1f861f=1658968627,1659323861; _trs_ua_s_1=l6aj0ztd_4085_elt8; Hm_lpvt_197b0a423d2d21ba532734d13a1f861f=1659348527; FSSBBIl1UgzbN7N80T=4qgQu8lSuOa9MyFFIo8Np2NPcrP0zmDP77mkhf6nTss4ppL2UBhhH3QhNy0qaN5YFETVIWebjZ5Y6zr8P7eJgx1AGn8h5sa2HfYJKky07v8duflR3PFxw9ycXVpwDP8cZ8YQ2OBdobKwZDHbl.BMzt_vLUqfFiWLybXjtfZ6ZwcoGsZEzmadDE_f6iPI_D_5U7FdUXXOEQ44WtsjBVGvKv.JtYb1WsQWAUv_tanTJpDH6D3q7T6y4H0C7WaNQgjjTzOXkmyJWZgo7L3911w4xvgrY2MizetGNhst61LNJTcpTlDqvQ05WxngWnSM4aAJ5FZej25Ya.53rgL07wMdK8Ff91prBopMOOlWb9hptqh8thd90tKixGmDvdjyoNIicIv7'
#
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'jycg_hubei_gov_cn.middlewares.JycgHubeiGovCnSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'jycg_hubei_gov_cn.middlewares.JycgHubeiGovCnDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'jycg_hubei_gov_cn.pipelines.Pipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
