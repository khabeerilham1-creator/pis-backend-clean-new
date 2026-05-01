from fastapi import APIRouter, HTTPException
from app.core.database import db
from jose import jwt
from datetime import datetime, timedelta
import hashlib

router = APIRouter()

users = db["users"]

SECRET_KEY = "secret123"
ALGORITHM = "HS256"


# =========================
# HASH FUNCTION (SAFE)
# =========================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: dict):

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing fields")

    if users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(password)

    users.insert_one({
        "username": username,
        "password": hashed
    })

    return {"msg": "User created"}


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    user = users.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if hash_password(password) != user["password"]:
        raise HTTPException(status_code=400, detail="Wrong password")

    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=10)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}