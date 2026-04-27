from pymongo import MongoClient

MONGO_URL = "mongodb://192.168.3.84:27017/"

client = MongoClient(MONGO_URL)

db = client["crawler_db"]

contents_collection = db["contents"]

def test_mongo():
    try:
        client.admin.command('ping')
        print("MongoDB successfully connected!")
    except Exception as e:
        print(f"Failed to connect MongoDB: {e}.")
