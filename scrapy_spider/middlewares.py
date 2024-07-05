from itemadapter import is_item, ItemAdapter
from scrapy import signals
from scrapy import signals
from scrapy.exceptions import IgnoreRequest


class ScrapySpiderSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ScrapySpiderDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ErrorHandlingMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def process_request(self, request, spider):
        # 在请求被下载器处理前的操作
        return None

    def process_response(self, request, response, spider):
        # 处理下载器返回的响应
        return response

    def process_exception(self, request, exception, spider):
        # 处理下载过程中的异常
        spider.logger.error('Error on request %s: %s' % (request.url, exception))
        # 可以根据异常类型进行不同的处理
        if isinstance(exception, IgnoreRequest):
            return None  # 忽略该请求
        # 处理其他异常
        return self._handle_other_exception(request, exception, spider)

    def _handle_other_exception(self, request, exception, spider):
        # 处理其他异常的具体逻辑
        # 这里可以进行重试、记录日志、发送通知等操作
        # 例如，可以重试请求
        new_request = request.copy()
        new_request.dont_filter = True  # 重试时避免过滤
        return new_request
