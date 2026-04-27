# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class WebpageItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    text_content = scrapy.Field()
    images = scrapy.Field() # 存储图片链接列表
    task_id = scrapy.Field() # A同学传给你的任务ID