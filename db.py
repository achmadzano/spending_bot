from pymongo import MongoClient
import os
from datetime import datetime
import pytz

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
    # Tambahkan field tanggal otomatis (waktu saat ini, Asia/Jakarta)
    tz = pytz.timezone('Asia/Jakarta')
    item['tanggal'] = datetime.now(tz)
    col.insert_one(item)

def get_all_items(user):
    col = get_collection(user)
    return list(col.find({}, {'_id': 0}))

def delete_item(item, user):
    col = get_collection(user)
    # Hapus satu item yang persis match nama dan harga
    col.delete_one({"nama": item["nama"], "harga": item["harga"]})

def get_monthly_recap(user):
    col = get_collection(user)
    pipeline = [
        {"$group": {
            "_id": {"year": {"$year": "$tanggal"}, "month": {"$month": "$tanggal"}},
            "total": {"$sum": {"$toInt": {"$replaceAll": {"input": "$harga", "find": ".", "replacement": ""}}}},
            "items": {"$push": {"nama": "$nama", "harga": "$harga", "tanggal": "$tanggal"}}
        }},
        {"$sort": {"_id.year": -1, "_id.month": -1}}
    ]
    return list(col.aggregate(pipeline))
