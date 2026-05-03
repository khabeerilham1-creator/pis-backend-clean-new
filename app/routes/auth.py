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
# HASH FUNCTION
# =========================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: dict):
    try:
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "staff")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing fields")

        if users.find_one({"username": username}):
            return {"msg": "User already exists"}

        users.insert_one({
            "username": username,
            "password": hash_password(password),  # 🔥 hashed
            "role": role
        })

        return {"msg": "User created"}

    except Exception as e:
        print("🔥 REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# LOGIN (SAFE + DEBUG)
# =========================
@router.post("/login")
def login(data: dict):
    try:
        print("LOGIN DATA:", data)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing credentials")

        user = users.find_one({"username": username})
        print("USER FOUND:", user)

        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        hashed_input = hash_password(password)
        print("INPUT HASH:", hashed_input)
        print("DB HASH:", user.get("password"))

        if hashed_input != user.get("password"):
            raise HTTPException(status_code=400, detail="Wrong password")

        payload = {
            "sub": user["username"],
            "role": user.get("role", "staff"),
            "exp": datetime.utcnow() + timedelta(hours=10)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": token,
            "role": user.get("role", "staff")
        }

    except Exception as e:
        print("🔥 LOGIN ERROR FULL:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# DELETE USER (TEMP DEBUG)
# =========================
@router.delete("/delete-user/{username}")
def delete_user(username: str):
    users.delete_one({"username": username})
    return {"msg": "User deleted"}