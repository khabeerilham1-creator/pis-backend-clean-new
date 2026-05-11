from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

APP_MODE = os.getenv("APP_MODE", "real")

REAL_DB = os.getenv("MONGO_URL")

if not REAL_DB:
    REAL_DB = "mongodb://localhost:27017"

DEMO_DB = os.getenv("DEMO_MONGO_URL")

if APP_MODE == "demo":

    print("🔥 DEMO DATABASE ACTIVE")

    client = MongoClient(DEMO_DB)

    db = client["smart_clinic_demo"]

else:

    print("✅ REAL DATABASE ACTIVE")

    client = MongoClient(REAL_DB)

    db = client["pis"]