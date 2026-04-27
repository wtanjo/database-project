import scrapy
from urllib.parse import urlparse
from datetime import datetime
from backend.crawler.crawler.items import WebpageMetaItem, ContentItem, ImageItem

class GeneralSpider(scrapy.Spider):
    name = 'crawler'
    
    def __init__(self, start_url=None, task_id=None, *args, **kwargs):
        super(GeneralSpider, self).__init__(*args, **kwargs)
        self.start_urls =[start_url] if start_url else[]
        self.task_id = task_id
        # 限制只在目标网站的域名下爬取
        if start_url:
            self.allowed_domains =[urlparse(start_url).netloc]

    def parse(self, response):
        # 仅处理 HTML 页面
        if not response.headers.get('Content-Type', b'').startswith(b'text/html'):
            return

        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        domain = urlparse(response.url).netloc

        # 1. 提取并生成元数据 (MySQL)
        meta_item = WebpageMetaItem()
        meta_item['domain'] = domain
        meta_item['url'] = response.url
        meta_item['title'] = response.css('title::text').get(default='').strip()
        meta_item['crawl_time'] = crawl_time
        meta_item['task_id'] = self.task_id
        yield meta_item

        # 2. 提取正文内容 (MongoDB)
        # 这里简单提取所有 <p> 标签作为正文，实际可接入 readability 等库
        paragraphs = response.css('p *::text').getall()
        text_content = '\n'.join([p.strip() for p in paragraphs if p.strip()])
        if text_content:
            content_item = ContentItem()
            content_item['webpage_url'] = response.url
            content_item['text_content'] = text_content
            content_item['keywords'] = [] # MVP 暂空，后续可接入 NLP 提取
            content_item['crawl_time'] = crawl_time
            yield content_item

        # 3. 提取图片信息 (MongoDB)
        images = response.css('img')
        for img in images:
            img_url = img.attrib.get('src')
            if img_url:
                img_item = ImageItem()
                img_item['webpage_url'] = response.url
                # 处理相对路径图片
                img_item['image_url'] = response.urljoin(img_url)
                img_item['description'] = img.attrib.get('alt', 'No Description')
                img_item['crawl_time'] = crawl_time
                yield img_item

        # 4. 自动跟进页面上的其他链接 (受 settings.py 的 DEPTH_LIMIT 限制)
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, callback=self.parse)