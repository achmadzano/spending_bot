from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://dudul:Zano0911@zano.7nzga4x.mongodb.net/")
DB_NAME = "spending_bot"
COLLECTION = "spending"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
col = db[COLLECTION]

def get_collection(user):
    if user == "juditemi":
        return db["spending_juditemi"]
    return db["spending_zano"]

def insert_item(item, user):
    col = get_collection(user)
    col.insert_one(item)

def get_all_items(user):
    col = get_collection(user)
    return list(col.find({}, {'_id': 0}))
