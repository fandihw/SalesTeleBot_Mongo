from dotenv import load_dotenv
import os

load_dotenv()

# BOT
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "sales_visit_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "visit_data")
USER_COLLECTION_NAME = os.getenv("USER_COLLECTION_NAME", "users")