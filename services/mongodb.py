from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, USER_COLLECTION_NAME

# WIB = UTC+7
WIB = timezone(timedelta(hours=7))

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
user_collection = db[USER_COLLECTION_NAME]

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

def get_all_data_last_30_days():
    """Ambil semua data 30 hari terakhir dari semua user untuk superadmin"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return list(
        collection.find({"timestamp": {"$gte": cutoff}})
                .sort("timestamp", -1)
    )

def get_data_from_yesterday():
    """Ambil semua data dari tanggal 1 kemarin sampai sekarang untuk superadmin"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return list(
        collection.find({"timestamp": {"$gte": yesterday}})
                .sort("timestamp", -1)
    )

def get_user_data_last_30_days(user_id: str):
    """Ambil data 30 hari terakhir untuk user tertentu"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return list(
        collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff}
        }).sort("timestamp", -1)
    )

def count_sales_last_30_days(sales_name: str):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return collection.count_documents({
        "sales_name": sales_name,
        "timestamp": {"$gte": cutoff}
    })

def is_user_allowed(user_id: int) -> bool:
    """Cek apakah user diizinkan menggunakan bot"""
    return user_collection.find_one({"telegram_id": str(user_id)}) is not None

def get_user_role(user_id: int) -> str:
    """Ambil role user dari database"""
    user = user_collection.find_one({"telegram_id": str(user_id)})
    if user:
        return user.get("role", "sales")  # default ke "sales" jika tidak ada role
    return None
