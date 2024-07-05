# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

class ScrapySpiderPipeline:
    def open_spider(self, spider):
        self.file = open('E:/PyCharm/scrapy_project/scrapy_spider/warehouse/output.csv', 'w', newline='',encoding='utf-8')  # 要限制编码格式，否则可能写入数据失败
        self.writer = csv.writer(self.file)
        self.writer.writerow(['url', 'text'])

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow([item['url'], item['text']])
        #self.writer.writerow([item.get('url'), ' '.join(item.get('text', []))])
        return item

