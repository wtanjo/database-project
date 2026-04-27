import pymysql
import pymongo
from datetime import datetime
# 记得导入新 Item
from crawler.items import WebpageMetaItem, ContentItem, ImageItem, TaskErrorItem

class DatabasePipeline:
    def __init__(self, mysql_cfg, mongo_cfg):
        self.mysql_cfg = mysql_cfg
        self.mongo_cfg = mongo_cfg
        self.task_id = None
        # --- 新增：错误标记，防止 close_spider 覆盖状态 ---
        self.error_occurred = False 

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_cfg=crawler.settings.get('MYSQL_SETTINGS'),
            mongo_cfg=crawler.settings.get('MONGO_SETTINGS')
        )

    def open_spider(self, spider):
        self.mysql_conn = pymysql.connect(**self.mysql_cfg)
        self.mysql_cursor = self.mysql_conn.cursor()
        self.mongo_client = pymongo.MongoClient(self.mongo_cfg['uri'])
        self.mongo_db = self.mongo_client[self.mongo_cfg['db_name']]
        
        self.task_id = getattr(spider, 'task_id', None)

        if self.task_id:
            update_sql = "UPDATE CrawlTask SET status='RUNNING' WHERE id=%s"
            self.mysql_cursor.execute(update_sql, (self.task_id,))
            self.mysql_conn.commit()

    def process_item(self, item, spider):
        # --- 新增：处理错误 Item ---
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
        """处理爬取错误，写入 MySQL"""
        self.error_occurred = True # 标记发生了错误
        if item['task_id']:
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_sql = """
                UPDATE CrawlTask 
                SET status='FAILED', error_msg=%s, finished_at=%s 
                WHERE id=%s
            """
            self.mysql_cursor.execute(update_sql, (
                item['error_msg'][:2048], # 截断防止超出字段长度
                finish_time, 
                item['task_id']
            ))
            self.mysql_conn.commit()

    def _process_mysql(self, item):
        # ... 你原有的插入 Website 和 Webpage 的逻辑 ...
        # (这里保持不变)
        site_sql = "INSERT IGNORE INTO Website (domain, created_at) VALUES (%s, %s)"
        self.mysql_cursor.execute(site_sql, (item['domain'], item['crawl_time']))
        
        self.mysql_cursor.execute("SELECT id FROM Website WHERE domain=%s", (item['domain'],))
        res = self.mysql_cursor.fetchone()
        if res:
            website_id = res[0]
            page_sql = """
                INSERT IGNORE INTO Webpage (url, website_id, crawl_time, status) 
                VALUES (%s, %s, %s, 'SUCCESS')
            """
            self.mysql_cursor.execute(page_sql, (item['url'], website_id, item['crawl_time']))
            self.mysql_conn.commit()

    def close_spider(self, spider):
        # --- 修改：只有在没有发生错误的情况下，才更新为 FINISHED ---
        if self.task_id and not self.error_occurred:
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_sql = "UPDATE CrawlTask SET status='FINISHED', finished_at=%s WHERE id=%s"
            self.mysql_cursor.execute(update_sql, (finish_time, self.task_id))
            self.mysql_conn.commit()

        self.mysql_cursor.close()
        self.mysql_conn.close()
        self.mongo_client.close()