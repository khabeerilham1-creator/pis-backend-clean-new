from fastapi import APIRouter, HTTPException
from app.core.database import db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

users = db["users"]

SECRET_KEY = "secret123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: dict):

    try:
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing fields")

        # check existing
        if users.find_one({"username": username}):
            raise HTTPException(status_code=400, detail="User already exists")

        # hash password
        hashed_password = pwd_context.hash(password)

        users.insert_one({
            "username": username,
            "password": hashed_password
        })

        return {"msg": "User created"}

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail="Register failed")


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: dict):

    try:
        username = data.get("username")
        password = data.get("password")

        user = users.find_one({"username": username})

        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        if not pwd_context.verify(password, user["password"]):
            raise HTTPException(status_code=400, detail="Wrong password")

        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(hours=10)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": token}

    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail="Login failed")