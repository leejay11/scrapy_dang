import csv
import json
import re
import sys
from collections import defaultdict

# 增加CSV字段大小限制
csv.field_size_limit(2**31-1)

def strip_html_tags(text):
    """去除文本中的HTML标签"""
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text

def clean_text(text):
    """清理文本，保留小于等于20个字符的纯文本内容"""
    text = strip_html_tags(text)
    segments = text.split('\t')
    clean_segments = [
        seg.strip() for seg in segments 
        if len(seg.strip()) <= 20 and seg.strip() and seg.strip() != '\n'
    ]
    return clean_segments

def process_csv_to_json(input_csv_files, output_json_file):
    data = defaultdict(set)  # 使用set自动去重
    
    for input_csv in input_csv_files:
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, fieldnames=['company_name', 'url', 'text_content'])
            next(reader, None)  # 跳过文件中的表头行

            for row in reader:
                company_name = row['company_name']
                text_content = row['text_content']
                # 去除文本中的 \n
                text_content = text_content.replace('\n', ' ')
                clean_segments = clean_text(text_content)
                if clean_segments:  # 只有在有有效内容时才添加
                    data[company_name].update(clean_segments)  # 使用update方法添加内容到set中，自动去重
    
    # 将合并后的数据写入JSON文件
    final_data = [
        {
            'company_name': company_name,
            'clean_text_content': list(clean_segments)  # 将set转换为list
        }
        for company_name, clean_segments in data.items()
    ]
    
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_csv_files = [
        'E:/PyCharm/scrapy_project/scrapy_spider/test_first_layer_links.csv',
        'E:/PyCharm/scrapy_project/scrapy_spider/test_second_layer_links.csv'
    ]
    output_json_file = 'E:/PyCharm/scrapy_project/scrapy_spider/test_cleaned_links.json'

    process_csv_to_json(input_csv_files, output_json_file)
