import scrapy
from urllib.parse import urlparse
from datetime import datetime
from backend.crawler.crawler.items import WebpageMetaItem, ContentItem, ImageItem

class GeneralSpider(scrapy.Spider):
    name = 'crawler'
    
    def __init__(self, start_url=None, task_id=None, *args, **kwargs):
        super(GeneralSpider, self).__init__(*args, **kwargs)
        # --- 修改 1: 显式保存 start_url 供下面使用 ---
        self.start_url = start_url 
        self.task_id = task_id
        
        if start_url:
            self.allowed_domains = [urlparse(start_url).netloc]

    def start_requests(self):
        if self.start_url:
            yield scrapy.Request(
                url=self.start_url,
                callback=self.parse,
                errback=self.errback_handler,
                meta={'task_id': self.task_id} # 初始传入
            )

    def errback_handler(self, failure):
        # --- 修改 2: 优先从 meta 获取 task_id，更健壮 ---
        task_id = failure.request.meta.get('task_id') or self.task_id
        self.logger.error(f"请求失败: {failure.request.url}, 错误: {str(failure.value)}")
        
        yield {
            'type': 'task_error',
            'task_id': task_id,
            'error_msg': str(failure.value),
            'status': 'failed'
        }

    def parse(self, response):
        # 提取当前请求携带的 task_id
        current_task_id = response.meta.get('task_id')

        if not response.headers.get('Content-Type', b'').startswith(b'text/html'):
            return

        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        domain = urlparse(response.url).netloc

        # 1. 提取元数据
        meta_item = WebpageMetaItem()
        meta_item['domain'] = domain
        meta_item['url'] = response.url
        meta_item['title'] = response.css('title::text').get(default='').strip()
        meta_item['crawl_time'] = crawl_time
        meta_item['task_id'] = current_task_id # 使用当前 meta 里的 id
        yield meta_item

        # 2. 提取正文 (逻辑保持不变)
        paragraphs = response.css('p *::text').getall()
        text_content = '\n'.join([p.strip() for p in paragraphs if p.strip()])
        if text_content:
            content_item = ContentItem()
            content_item['webpage_url'] = response.url
            content_item['text_content'] = text_content
            content_item['keywords'] = []
            content_item['crawl_time'] = crawl_time
            yield content_item

        # 3. 提取图片 (逻辑保持不变)
        images = response.css('img')
        for img in images:
            img_url = img.attrib.get('src')
            if img_url:
                img_item = ImageItem()
                img_item['webpage_url'] = response.url
                img_item['image_url'] = response.urljoin(img_url)
                img_item['description'] = img.attrib.get('alt', 'No Description')
                img_item['crawl_time'] = crawl_time
                yield img_item

        # --- 修改 3: 自动跟进链接时，必须手动传递 errback 和 meta ---
        for href in response.css('a::attr(href)').getall():
            yield response.follow(
                href, 
                callback=self.parse, 
                errback=self.errback_handler, # 必须重复指定
                meta={'task_id': current_task_id} # 必须手动向下传递
            )