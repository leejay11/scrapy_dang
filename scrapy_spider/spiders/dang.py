import csv
from urllib.parse import urlparse, urljoin

import chardet
import scrapy
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
import signal
from twisted.internet import reactor
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
import subprocess

from scrapy_spider.items import ScrapySpiderItem


class DangSpider(Spider):
    name = "dang"


    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 8,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'RETRY_TIMES': 3,  # 不重试
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
        },
        'ITEM_PIPELINES': {
            'scrapy_spider.pipelines.ScrapySpiderPipeline': 300,
        },
    }

    def __init__(self, depth=2, *args, **kwargs):
        super(DangSpider, self).__init__(*args, **kwargs)
        self.depth = depth
        self.start_urls = []
        self.allowed_domains = set()
        self.company_urls = []
        self.load_urls_and_domains()
        self.load_blacklist()
        self.load_whitelist()
        self.load_target_keys()

        # 设置信号处理函数
        signal.signal(signal.SIGINT, self.handle_sigint)

    # def load_urls_and_domains(self):
    #     with open('E:/PyCharm/scrapy_project/scrapy_spider/warehouse/test_url.csv', 'r',encoding='utf-8') as f:
    #         reader = csv.DictReader(f)
    #         for row in reader:
    #             company_name = row['name']
    #             url = row['url']
    #             if not urlparse(url).scheme:
    #                 url = 'https://' + url
    #             self.company_urls.append((company_name, url))
    #             domain = urlparse(url).netloc
    #             self.allowed_domains.add(domain)
    #     self.allowed_domains = list(self.allowed_domains)

    # 检测文件编码格式
    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']

    def load_urls_and_domains(self):
        file_path = 'E:/PyCharm/scrapy_project/scrapy_spider/warehouse/test_url.csv'
        encoding = self.detect_encoding(file_path)
        print(f"Detected encoding: {encoding}")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(f"Read row: {row}")
                    company_name = row['name']
                    url = row['url']
                    if not urlparse(url).scheme:
                        url = 'https://' + url
                    self.company_urls.append((company_name, url))
                    domain = urlparse(url).netloc
                    self.allowed_domains.add(domain)
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError with detected encoding: {encoding} - {str(e)}")
        except KeyError as e:
            print(f"KeyError: Missing key in row - {str(e)}")
        except Exception as e:
            print(f"Unhandled exception: {str(e)}")

        self.allowed_domains = list(self.allowed_domains)

    def load_blacklist(self):
        with open('E:/PyCharm/scrapy_project/scrapy_spider/warehouse/black.txt', 'r',encoding='utf-8') as f:
            self.blacklist = [line.strip() for line in f]

    def load_whitelist(self):
        with open('E:/PyCharm/scrapy_project/scrapy_spider/warehouse/white.txt', 'r',encoding='utf-8') as f:
            self.whitelist = [line.strip() for line in f]

    def load_target_keys(self):
        with open('E:/PyCharm/scrapy_project/scrapy_spider/warehouse/key.txt', 'r') as f:
            self.target_keys = [line.strip() for line in f]

    def start_requests(self):
        for company_name, url in self.company_urls:
            # 通过日志记录来检查是否发出了初始请求。
            self.logger.info(f"Starting request for {company_name} at {url}")
            yield scrapy.Request(url=url, callback=self.parse_initial, errback=self.errorback, meta={'company_name': company_name})

    def parse_initial(self, response):
        company_name = response.meta['company_name']
        text_content = self.extract_text(response)

        self.logger.info(f"Parsing initial page for {company_name} at {response.url}")

        with open('E:/PyCharm/scrapy_project/scrapy_spider/test_first_layer_links.csv', 'a', newline='',encoding='utf-8') as f:
            fieldnames = ['company_name', 'url', 'text_content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'company_name': company_name, 'url': response.url, 'text_content': text_content})

            self.logger.info(f"Wrote to CSV for {company_name} at {response.url}")

            # item传递
            item = ScrapySpiderItem()
            item['url'] = response.url
            item['text'] = text_content
            yield item

        links = response.css('a::attr(href)').extract()
        if self.depth > 1:
            for link in links:
                full_url = urljoin(response.url, link)
                if self.should_follow_link(full_url):
                    yield scrapy.Request(url=full_url, callback=self.parse_second_layer, errback=self.errorback, meta={'company_name': company_name})

    def parse_second_layer(self, response):
        company_name = response.meta['company_name']
        text_content = self.extract_text(response)

        # item传递
        item = ScrapySpiderItem()
        item['url'] = response.url
        item['text'] = text_content
        yield item

        with open('E:/PyCharm/scrapy_project/scrapy_spider/test_second_layer_links.csv', 'a', newline='',encoding='utf-8') as f:
            fieldnames = ['company_name', 'url', 'text_content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'company_name': company_name, 'url': response.url, 'text_content': text_content})

        links = response.css('a::attr(href)').extract()
        if self.depth > 2:
            for link in links:
                full_url = urljoin(response.url, link)
                if self.should_follow_link(full_url):
                    yield scrapy.Request(url=full_url, callback=self.parse_third_layer, errback=self.errorback, meta={'company_name': company_name})

    def parse_third_layer(self, response):
        company_name = response.meta['company_name']
        text_content = self.extract_text(response)

        # item传递
        item = ScrapySpiderItem()
        item['url'] = response.url
        item['text'] = text_content
        yield item

        with open('E:/PyCharm/scrapy_project/scrapy_spider/test_third_layer_links.csv', 'a', newline='',encoding='utf-8') as f:
            fieldnames = ['company_name', 'url', 'text_content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'company_name': company_name, 'url': response.url, 'text_content': text_content})

    def extract_text(self, response):
        clean_body = response.xpath('//body//text()[not(ancestor::script) and not(ancestor::style)]').getall()
        text_content = ' '.join(clean_body).strip()
        self.logger.info(f"Extracted text content for {response.url}: {text_content[:100]}...")  # 仅显示前100个字符进行调试
        return text_content

    def should_follow_link(self, url):
        """判断是否应该跟随链接"""
        for term in self.blacklist:
            if term in url:
                return False
        for term in self.whitelist:
            if term in url:
                return True
        for term in self.target_keys:
            if term in url:
                return True
        return False

    def handle_sigint(self, signum, frame):
        """处理中断信号"""
        # reactor.stop()  # 停止 Reactor
        pass

    def errorback(self, failure):
        self.logger.error(f"Error on request {failure.request.url}: {failure.value}. Skipping request.")
        return
