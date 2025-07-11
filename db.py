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
    # Setiap user punya collection sendiri, nama: spending_<username>
    return db[f"spending_{user}"]

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

def get_target_bulan_ini(user, tahun, bulan):
    target_col = db["spending_target"]
    doc = target_col.find_one({"user": user, "tahun": tahun, "bulan": bulan})
    return doc["target"] if doc else None

def set_target_bulan_ini(user, tahun, bulan, target):
    target_col = db["spending_target"]
    target_col.update_one(
        {"user": user, "tahun": tahun, "bulan": bulan},
        {"$set": {"target": target}},
        upsert=True
    )

def register_user(username, password):
    user_col = db["users"]
    if user_col.find_one({"username": username}):
        return False  # Username sudah ada
    user_col.insert_one({"username": username, "password": password})
    return True

def authenticate_user(username, password):
    user_col = db["users"]
    user = user_col.find_one({"username": username, "password": password})
    return user is not None
