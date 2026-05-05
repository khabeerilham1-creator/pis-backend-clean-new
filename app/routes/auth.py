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
# HASH FUNCTION (SHA256)
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

        existing = users.find_one({"username": username})
        if existing:
            return {"msg": "User already exists"}

        users.insert_one({
            "username": username,
            "password": hash_password(password),   # ✅ SHA256
            "role": role
        })

        return {"msg": "User created ✅"}

    except Exception as e:
        print("🔥 REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: dict):
    try:
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing credentials")

        user = users.find_one({"username": username})

        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # ✅ HASH INPUT PASSWORD
        hashed_input = hash_password(password)

        # 🔥 SAFE CHECK
        db_password = user.get("password")

        if not db_password:
            raise HTTPException(status_code=500, detail="User password missing")

        if hashed_input != db_password:
            raise HTTPException(status_code=400, detail="Wrong password")

        # =========================
        # TOKEN
        # =========================
        payload = {
            "sub": user["username"],
            "role": user.get("role", "staff"),
            "exp": datetime.utcnow() + timedelta(hours=10)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": token,
            "role": user.get("role", "staff"),
            "username": user.get("username")
        }

    except HTTPException:
        raise

    except Exception as e:
        print("🔥 LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# DELETE USER
# =========================
@router.delete("/delete-user/{username}")
def delete_user(username: str):
    users.delete_one({"username": username})
    return {"msg": "User deleted"}