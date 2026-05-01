from fastapi import APIRouter, HTTPException
from app.core.database import db
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib

router = APIRouter()

users = db["users"]

SECRET_KEY = "secret123"
ALGORITHM = "HS256"


# =========================
# SCHEMA
# =========================
class UserCreate(BaseModel):
    username: str
    password: str


# =========================
# HASH FUNCTION
# =========================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: UserCreate):

    try:
        username = data.username
        password = data.password

        if users.find_one({"username": username}):
            return {"msg": "User already exists"}

        hashed = hash_password(password)

        users.insert_one({
            "username": username,
            "password": hashed
        })

        return {"msg": "User created"}

    except Exception as e:
        print("🔥 REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: UserCreate):

    try:
        username = data.username
        password = data.password

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

    except Exception as e:
        print("🔥 LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))