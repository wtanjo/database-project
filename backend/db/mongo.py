from pymongo import MongoClient
from crawler.crawler.settings import MONGO_SETTINGS as ms

MONGO_URL = ms['uri']
client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000,
    maxPoolSize=10,
)

db = client[ms['db_name']]

contents_collection = db["contents"]
images_collection = db["images"]

# 创建索引以优化查询性能
contents_collection.create_index("webpage_url", background=True)
contents_collection.create_index("crawl_time", background=True)
images_collection.create_index("webpage_url", background=True)
images_collection.create_index("crawl_time", background=True)

def test_mongo():
    try:
        client.admin.command('ping')
        print("MongoDB successfully connected!")
    except Exception as e:
        print(f"Failed to connect MongoDB: {e}.")
