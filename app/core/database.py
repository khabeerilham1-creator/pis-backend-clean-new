from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def connect_db():
    try:
        client.admin.command("ping")
        print("MongoDB Connected ✅")
    except Exception as e:
        print("MongoDB Connection Failed ❌", e)