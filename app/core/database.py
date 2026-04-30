from pymongo import MongoClient
import os

# ✅ Use environment variable (Render)
MONGO_URL = os.getenv("MONGO_URL")

# fallback (optional for local)
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

# ✅ database name
db = client["pis"]