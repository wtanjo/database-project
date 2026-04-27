import pymysql
import pymongo
from backend.crawler.crawler.items import WebpageMetaItem, ContentItem, ImageItem

class DatabasePipeline:
    def __init__(self, mysql_cfg, mongo_cfg):
        self.mysql_cfg = mysql_cfg
        self.mongo_cfg = mongo_cfg
        self.task_id = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_cfg=crawler.settings.get('MYSQL_SETTINGS'),
            mongo_cfg=crawler.settings.get('MONGO_SETTINGS')
        )

    def open_spider(self, spider):
        # 初始化 MySQL 连接
        self.mysql_conn = pymysql.connect(**self.mysql_cfg)
        self.mysql_cursor = self.mysql_conn.cursor()
        
        # 初始化 MongoDB 连接
        self.mongo_client = pymongo.MongoClient(self.mongo_cfg['uri'])
        self.mongo_db = self.mongo_client[self.mongo_cfg['db_name']]
        
        # 获取 FastAPI 传进来的 task_id
        self.task_id = getattr(spider, 'task_id', None)

        # 【MySQL】更新任务状态为正在爬取
        if self.task_id:
            update_sql = "UPDATE CrawlTask SET status='RUNNING' WHERE id=%s"
            self.mysql_cursor.execute(update_sql, (self.task_id,))
            self.mysql_conn.commit()

    def process_item(self, item, spider):
        if isinstance(item, WebpageMetaItem):
            # 处理 MySQL 数据
            self._process_mysql(item)
        elif isinstance(item, ContentItem):
            # 处理 MongoDB 正文数据
            self.mongo_db['contents'].insert_one(dict(item))
        elif isinstance(item, ImageItem):
            # 处理 MongoDB 图片数据
            self.mongo_db['images'].insert_one(dict(item))
        return item

    def _process_mysql(self, item):
        # 1. 插入 Website (忽略重复)
        site_sql = """
            INSERT IGNORE INTO Website (domain, created_at) 
            VALUES (%s, %s)
        """
        self.mysql_cursor.execute(site_sql, (item['domain'], item['crawl_time']))
        
        # 获取 website_id
        self.mysql_cursor.execute("SELECT id FROM Website WHERE domain=%s", (item['domain'],))
        website_id = self.mysql_cursor.fetchone()[0]

        # 2. 插入 Webpage (忽略重复)
        page_sql = """
            INSERT IGNORE INTO Webpage (url, website_id, crawl_time, status) 
            VALUES (%s, %s, %s, 'SUCCESS')
        """
        self.mysql_cursor.execute(page_sql, (item['url'], website_id, item['crawl_time']))
        self.mysql_conn.commit()

    def close_spider(self, spider):
        # 【MySQL】爬取结束，更新任务状态
        if self.task_id:
            from datetime import datetime
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_sql = "UPDATE CrawlTask SET status='FINISHED', finished_at=%s WHERE id=%s"
            self.mysql_cursor.execute(update_sql, (finish_time, self.task_id))
            self.mysql_conn.commit()

        self.mysql_cursor.close()
        self.mysql_conn.close()
        self.mongo_client.close()