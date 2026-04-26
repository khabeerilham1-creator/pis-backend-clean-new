from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# 🔥 DATABASE
client = MongoClient("mongodb+srv://khabeerilham1_db_user:Khabeer2007@cluster0.f81lede.mongodb.net/?appName=Cluster0")
db = client["pis"]
users_collection = db["users"]

# 🔥 CORS (FINAL FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clinic-client-lake.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 🔥 PREFLIGHT HANDLER (VERY IMPORTANT)
@app.options("/{full_path:path}")
async def preflight_handler(request: Request):
    return {}

# ROOT
@app.get("/")
def root():
    return {"message": "API running"}

# LOGIN
@app.post("/auth/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user["password"] != password:
        raise HTTPException(status_code=401, detail="Wrong password")

    if not user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Not approved")

    return {
        "access_token": "dummy_token",
        "user": username
    }

# REGISTER
@app.post("/auth/register")
def register(data: dict):
    users_collection.insert_one({
        "username": data.get("username"),
        "password": data.get("password"),
        "role": data.get("role", "user"),
        "is_approved": False
    })

    return {"message": "User registered, wait for approval"}

# GET PENDING USERS
@app.get("/users/pending")
def get_pending():
    users = list(users_collection.find({"is_approved": False}))
    for u in users:
        u["_id"] = str(u["_id"])
    return users

# APPROVE USER
@app.put("/users/approve/{user_id}")
def approve(user_id: str):
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_approved": True}}
    )
    return {"message": "User approved"}