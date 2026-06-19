import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

APP_MODE = os.getenv("APP_MODE", "real").lower()
REAL_DB_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DEMO_DB_URL = os.getenv("DEMO_MONGO_URL", REAL_DB_URL)

if APP_MODE == "demo":
    mongo_url = DEMO_DB_URL
    database_name = os.getenv("DEMO_DB_NAME", "smart_clinic_demo")
    print("DEMO DATABASE ACTIVE")
else:
    mongo_url = REAL_DB_URL
    database_name = os.getenv("DB_NAME", "pis")
    print("REAL DATABASE ACTIVE")

client = MongoClient(
    mongo_url,
    serverSelectionTimeoutMS=5000,
)

db = client[database_name]


def ensure_indexes():
    try:
        db.patients.create_index("biography.regNo", unique=True, sparse=True)
        db.patients.create_index("biography.patientName")
        db.patients.create_index("biography.mobileNumber")
        db.patients.create_index("createdAt")
        db.inventory.create_index("productName")
        db.inventory.create_index("date")
        db.expenses.create_index("category")
        db.expenses.create_index("date")
        db.expenses.create_index("expenseName")
    except Exception as exc:
        print(f"Database index setup skipped: {exc}")


ensure_indexes()
