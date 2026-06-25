import scrapy
from urllib.parse import urlparse
from datetime import datetime, timezone
from crawler.items import WebpageMetaItem, ContentItem, ImageItem, TaskErrorItem


class GeneralSpider(scrapy.Spider):
    name = "crawler"

    def __init__(self, start_url=None, task_id=None, *args, **kwargs):
        super(GeneralSpider, self).__init__(*args, **kwargs)
        self.start_url = start_url
        # Coerce task_id to int (Scrapy -a flag passes everything as string)
        self.task_id = int(task_id) if task_id else None

        if start_url:
            parsed = urlparse(start_url)
            if not parsed.netloc:
                self.logger.error(f"无法解析域名: {start_url}")
                self.allowed_domains = []
            else:
                self.allowed_domains = [parsed.netloc]

    def start_requests(self):
        if self.start_url:
            yield scrapy.Request(
                url=self.start_url,
                callback=self.parse,
                errback=self.errback_handler,
                meta={"task_id": self.task_id},  # 初始传入
            )

    def errback_handler(self, failure):
        task_id = failure.request.meta.get("task_id") or self.task_id
        self.logger.error(
            f"请求失败: {failure.request.url}, 错误: {str(failure.value)}"
        )

        error_item = TaskErrorItem()
        error_item["task_id"] = task_id
        error_item["error_msg"] = str(failure.value)
        error_item["status"] = "failed"
        yield error_item

    def parse(self, response):
        # 提取当前请求携带的 task_id
        current_task_id = response.meta.get("task_id")

        # 检查 Content-Type：缺失时也继续处理（部分服务器不返回该头）
        content_type = response.headers.get("Content-Type", b"")
        if content_type and not content_type.startswith(b"text/html"):
            self.logger.debug(
                f"跳过非 HTML 响应: {response.url} (Content-Type: {content_type})"
            )
            return

        crawl_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        domain = urlparse(response.url).netloc

        # 1. 提取元数据
        meta_item = WebpageMetaItem()
        meta_item["domain"] = domain
        meta_item["url"] = response.url
        meta_item["title"] = response.css("title::text").get(default="").strip()
        meta_item["crawl_time"] = crawl_time
        meta_item["task_id"] = current_task_id  # 使用当前 meta 里的 id
        yield meta_item

        # 2. 提取正文：用 XPath 抓取 body 内所有可见文本节点，排除 script/style
        #    限制在 2MB 以内防止 MongoDB BSON 16MB 溢出
        text_nodes = response.xpath(
            "//body//text()[not(ancestor::script) and not(ancestor::style)]"
        ).getall()
        text_content = "\n".join([t.strip() for t in text_nodes if t.strip()])
        if text_content:
            MAX_TEXT = 2 * 1024 * 1024  # 2 MB
            if len(text_content.encode("utf-8")) > MAX_TEXT:
                text_content = text_content.encode("utf-8")[:MAX_TEXT].decode(
                    "utf-8", errors="ignore"
                )
                self.logger.warning(f"正文过长已截断: {response.url}")
            content_item = ContentItem()
            content_item["webpage_url"] = response.url
            content_item["text_content"] = text_content
            content_item["keywords"] = []
            content_item["crawl_time"] = crawl_time
            yield content_item

        # 3. 提取图片 (逻辑保持不变)
        images = response.css("img")
        for img in images:
            img_url = img.attrib.get("src")
            if img_url:
                img_item = ImageItem()
                img_item["webpage_url"] = response.url
                img_item["image_url"] = response.urljoin(img_url)
                img_item["description"] = img.attrib.get("alt", "No Description")
                img_item["crawl_time"] = crawl_time
                yield img_item

        # 自动跟进链接（过滤无效 scheme）
        INVALID_SCHEMES = {"mailto:", "javascript:", "tel:", "ftp:", "data:", "file:"}
        for href in response.css("a::attr(href)").getall():
            href = href.strip()
            if not href:
                continue
            lower = href.lower()
            if any(lower.startswith(s) for s in INVALID_SCHEMES) or lower.startswith(
                "#"
            ):
                continue
            req = response.follow(
                href,
                callback=self.parse,
                errback=self.errback_handler,
                meta={"task_id": current_task_id},
            )
            if req is not None:
                yield req
