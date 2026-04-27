from pymongo import MongoClient
from crawler.crawler.settings import MYSQL_SETTINGS as ms

MONGO_URL = f"mongodb://{ms['host']}:{ms['port']}/"

client = MongoClient(MONGO_URL)

db = client["crawler_db"]

contents_collection = db["contents"]

def test_mongo():
    try:
        client.admin.command('ping')
        print("MongoDB successfully connected!")
    except Exception as e:
        print(f"Failed to connect MongoDB: {e}.")
