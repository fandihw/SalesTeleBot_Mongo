from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

# WIB = UTC+7
WIB = timezone(timedelta(hours=7))

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_data(user_data: dict):
    doc = user_data.copy()
    doc["timestamp"] = datetime.now(timezone.utc)  # ✅ simpan sebagai UTC
    collection.insert_one(doc)

def get_last_30_days_data():
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return list(
        collection.find({"timestamp": {"$gte": cutoff}})
                .sort("timestamp", -1)
                .limit(30)
    )

def count_sales_last_30_days(sales_name: str):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return collection.count_documents({
        "sales_name": sales_name,
        "timestamp": {"$gte": cutoff}
    })
