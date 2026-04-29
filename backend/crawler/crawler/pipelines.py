import pymysql
import pymongo
from datetime import datetime
from crawler.items import WebpageMetaItem, ContentItem, ImageItem, TaskErrorItem


class DatabasePipeline:
    def __init__(self, mysql_cfg, mongo_cfg):
        self.mysql_cfg = mysql_cfg
        self.mongo_cfg = mongo_cfg
        self.task_id = None
        self.error_occurred = False
        self.page_count = 0  # 统计本次爬取的网页数

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_cfg=crawler.settings.get('MYSQL_SETTINGS'),
            mongo_cfg=crawler.settings.get('MONGO_SETTINGS'),
        )

    def open_spider(self, spider):
        self.mysql_conn = pymysql.connect(**self.mysql_cfg)
        self.mysql_cursor = self.mysql_conn.cursor()
        self.mongo_client = pymongo.MongoClient(self.mongo_cfg['uri'])
        self.mongo_db = self.mongo_client[self.mongo_cfg['db_name']]
        self.task_id = getattr(spider, 'task_id', None)

        if self.task_id:
            self.mysql_cursor.execute(
                "UPDATE CrawlTask SET status='running' WHERE id=%s",
                (self.task_id,),
            )
            self.mysql_conn.commit()

    def process_item(self, item, spider):
        if isinstance(item, TaskErrorItem):
            self._handle_task_error(item)
            return item

        if isinstance(item, WebpageMetaItem):
            self._process_mysql(item)
        elif isinstance(item, ContentItem):
            self.mongo_db['contents'].insert_one(dict(item))
        elif isinstance(item, ImageItem):
            self.mongo_db['images'].insert_one(dict(item))
        return item

    def _handle_task_error(self, item):
        self.error_occurred = True
        if item['task_id']:
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.mysql_cursor.execute(
                "UPDATE CrawlTask SET status='failed', error_msg=%s, finished_at=%s WHERE id=%s",
                (item['error_msg'][:2048], finish_time, item['task_id']),
            )
            self.mysql_conn.commit()

    def _process_mysql(self, item):
        # 写入 Website（忽略重复）
        self.mysql_cursor.execute(
            "INSERT IGNORE INTO Website (domain, created_at) VALUES (%s, %s)",
            (item['domain'], item['crawl_time']),
        )

        self.mysql_cursor.execute(
            "SELECT id FROM Website WHERE domain=%s",
            (item['domain'],),
        )
        res = self.mysql_cursor.fetchone()
        if res:
            website_id = res[0]
            # 写入 Webpage（忽略重复），同时插入 title
            self.mysql_cursor.execute(
                """INSERT IGNORE INTO Webpage (url, website_id, crawl_time, status, title)
                   VALUES (%s, %s, %s, 'success', %s)""",
                (item['url'], website_id, item['crawl_time'], item.get('title', '')),
            )
            affected = self.mysql_cursor.rowcount
            self.mysql_conn.commit()
            if affected > 0:
                self.page_count += 1

    def close_spider(self, spider):
        if self.task_id and not self.error_occurred:
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.mysql_cursor.execute(
                "UPDATE CrawlTask SET status='completed', finished_at=%s, page_count=%s WHERE id=%s",
                (finish_time, self.page_count, self.task_id),
            )
            self.mysql_conn.commit()

        self.mysql_cursor.close()
        self.mysql_conn.close()
        self.mongo_client.close()
