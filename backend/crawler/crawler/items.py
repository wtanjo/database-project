import scrapy

class WebpageMetaItem(scrapy.Item):
    """存入 MySQL 的网页元数据"""
    domain = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    crawl_time = scrapy.Field()
    task_id = scrapy.Field()

class ContentItem(scrapy.Item):
    """存入 MongoDB 的正文内容"""
    webpage_url = scrapy.Field()
    text_content = scrapy.Field()
    keywords = scrapy.Field()
    crawl_time = scrapy.Field()

class ImageItem(scrapy.Item):
    """存入 MongoDB 的图片数据"""
    webpage_url = scrapy.Field()
    image_url = scrapy.Field()
    description = scrapy.Field()
    crawl_time = scrapy.Field()

class TaskErrorItem(scrapy.Item):
    """专门用于传递爬取过程中的错误信息"""
    task_id = scrapy.Field()
    error_msg = scrapy.Field()
    status = scrapy.Field()  # 通常为 'FAILED'