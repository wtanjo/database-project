import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class GeneralSpider(scrapy.Spider):
    name = "general_spider"

    def __init__(self, start_url=None, task_id=None, *args, **kwargs):
        super(GeneralSpider, self).__init__(*args, **kwargs)
        # 这两个参数是由 FastAPI 传进来的
        self.start_urls = [start_url] if start_url else []
        self.task_id = task_id
        
        # 为了防止爬虫跑飞，可以限制只爬取当前域名
        if start_url:
            self.allowed_domains = [start_url.split("//")[-1].split("/")[0]]

    def parse(self, response):
        """
        核心解析逻辑：抓取网页的结构化信息和内容
        """
        # 1. 提取网页基本信息
        title = response.css('title::text').get() or response.xpath('//h1/text()').get()
        
        # 2. 提取正文内容（简单处理：获取所有 p 标签的文本）
        paragraphs = response.css('p::text').getall()
        text_content = "\n".join([p.strip() for p in paragraphs if p.strip()])

        # 3. 提取所有图片链接
        # 考虑到相对路径，使用 response.urljoin 转换为绝对路径
        images = []
        for img in response.css('img::attr(src)').getall():
            images.append(response.urljoin(img))

        # 4. 打包数据，交给 Pipeline 处理
        # 这些数据会被发送到 pipelines.py
        yield {
            'task_id': self.task_id,
            'url': response.url,
            'title': title.strip() if title else "No Title",
            'text_content': text_content,
            'images': images,
            'crawl_time': scrapy.utils.project.get_project_settings().get('LOG_DATEFORMAT') 
        }

        # 5. 可选：如果你想爬取这个页面上的其他链接（深度爬取）
        # 这里仅作演示，MVP阶段可以先注释掉
        # link_extractor = LinkExtractor(allow_domains=self.allowed_domains)
        # for link in link_extractor.extract_links(response):
        #     yield scrapy.Request(link.url, callback=self.parse)