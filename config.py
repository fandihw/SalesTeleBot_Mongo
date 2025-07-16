from dotenv import load_dotenv
import os

load_dotenv()

# BOT
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "sales_visit_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "visit_data")

ALLOWED_USER_IDS = {
    1825371102,
}

# ────────────── Admin ──────────────
ADMIN_IDS = {
    1825371102,
}