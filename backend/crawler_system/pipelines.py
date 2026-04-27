# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo

class MongoPipeline:
    def __init__(self):
        # Docker 内部通过服务名 'mongo' 访问
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["crawler_db"]

    def process_item(self, item, spider):
        # 存储到 contents 集合
        self.db["contents"].insert_one(dict(item))
        return item
