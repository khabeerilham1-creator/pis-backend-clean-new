from fastapi import APIRouter, HTTPException
from app.core.database import db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter()

users = db["users"]

SECRET_KEY = "hdc_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PASSWORD
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# TOKEN
def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=8)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================= REGISTER =================
@router.post("/register")
async def register(data: dict):

    username = data.get("username")
    password = data.get("password")

    if users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="User exists")

    users.insert_one({
        "username": username,
        "password": hash_password(password),
        "role": data.get("role", "office"),
        "is_approved": False  # 🔥 KEY
    })

    return {"msg": "Registered. Wait for admin approval."}


# ================= LOGIN =================
@router.post("/login")
async def login(data: dict):

    user = users.find_one({"username": data["username"]})

    if not user or not verify_password(data["password"], user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 🔥 APPROVAL CHECK
    if not user.get("is_approved", False):
        raise HTTPException(status_code=403, detail="Waiting for admin approval")

    token = create_token({
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "role": user["role"]
    }


# ================= GET PENDING USERS =================
@router.get("/users/pending")
def get_pending():
    data = []
    for u in users.find({"is_approved": False}):
        u["_id"] = str(u["_id"])
        data.append(u)
    return data


# ================= APPROVE USER =================
@router.put("/users/approve/{id}")
def approve_user(id: str):
    users.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"is_approved": True}}
    )
    return {"msg": "User approved"}