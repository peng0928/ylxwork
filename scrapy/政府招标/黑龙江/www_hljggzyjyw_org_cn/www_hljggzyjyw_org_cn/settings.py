# Scrapy settings for www_hljggzyjyw_org_cn project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'www_hljggzyjyw_org_cn'
SPIDER_MODULES = ['www_hljggzyjyw_org_cn.spiders']
NEWSPIDER_MODULE = 'www_hljggzyjyw_org_cn.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'www_hljggzyjyw_org_cn (+http://www.yourdomain.com)'

# Obey robots.txt rules


# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
# 'Accept-Encoding': 'gzip, deflate',
# 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
# 'Connection': 'keep-alive',
# 'Cookie': 'Secure; Secure; Secure; _gscu_1770828364=59671364tib2ht14; _gscbrs_1770828364=1; userGuid=-2001935666; oauthPath=http://127.0.0.1:8080/EpointWebBuilder; oauthClientId=demoClient; oauthLoginUrl=http://127.0.0.1:8080/EpointWebBuilder/rest/oauth2/authorize?client_id=demoClient&state=a&response_type=code&scope=user&redirect_uri=; oauthLogoutUrl=http://127.0.0.1:8080/EpointWebBuilder/rest/oauth2/logout?redirect_uri=; noOauthAccessToken=a7f749aee211e4311455a228ff6d4df2; noOauthRefreshToken=73a409d707e27b535ee002a03d59e97e; Secure; _gscs_1770828364=59671364ubbc8114|pv:61',
# 'Host': 'www.hljggzyjyw.org.cn',
# 'If-Modified-Since': 'Fri, 05 Aug 2022 04:20:01 GMT',
# 'If-None-Match': 'W/"62ec9a71-e818"',
# 'Referer': 'http://www.hljggzyjyw.org.cn/jyfwdt/003002/003002002/003002002001/about2.html?categoryNum=003002002001&pageIndex=1',
# 'Upgrade-Insecure-Requests': '1',
# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
#
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'www_hljggzyjyw_org_cn.middlewares.WwwHljggzyjywOrgCnSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'www_hljggzyjyw_org_cn.middlewares.WwwHljggzyjywOrgCnDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html


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



# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html


# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy_splash.SplashCookiesMiddleware': 723,
#     'scrapy_splash.SplashMiddleware': 725,
#     'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,  # 不配置查不到信息
# }
#
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
#
# SPLASH_URL = "http://10.0.3.14:8050/"  # 自己安装的docker里的splash位置
# # DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'