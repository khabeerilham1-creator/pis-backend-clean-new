from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise Exception("MONGO_URL not set")

client = MongoClient(MONGO_URL)

# ✅ FIXED (NO ENV NEEDED)
db = client["pis_db"]