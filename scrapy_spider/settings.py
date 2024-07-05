# Scrapy settings for scrapy_spider project
BOT_NAME = 'scrapy_spider'

SPIDER_MODULES = ['scrapy_spider.spiders']
NEWSPIDER_MODULE = 'scrapy_spider.spiders'
#TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'  # 解决多线程问题

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'scrapy_spider.pipelines.ScrapySpiderPipeline': 300,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawler.middlewares.ProxyTunnelMiddleware': 700,
    'scrapy_crawler.middlewares.CloseConnectionMiddleware': 690,
    'scrapy_crawler.middlewares.DownloadExceptionMiddleware': 543,
}
# settings.py

LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# 全局并发请求数
CONCURRENT_REQUESTS = 32

# 每个域名的并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 16

# 每个 IP 的并发请求数
CONCURRENT_REQUESTS_PER_IP = 16

# 调整 Twisted 线程池大小
REACTOR_THREADPOOL_MAXSIZE = 20

from twisted.internet import reactor

def configure_reactor():
    reactor.suggestThreadPoolSize(REACTOR_THREADPOOL_MAXSIZE)

# 将配置函数添加到 Scrapy 启动的钩子中
configure_reactor()

# 并发设置
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16

# 其他设置
#TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

