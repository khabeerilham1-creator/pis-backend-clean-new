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

    if users.find_one({"username": data["username"]}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(data["password"])

    users.insert_one({
        "username": data["username"],
        "password": hashed_password
    })

    return {"msg": "User created"}


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: dict):

    user = users.find_one({"username": data["username"]})

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not pwd_context.verify(data["password"], user["password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    # 🔥 CREATE REAL JWT TOKEN
    payload = {
        "sub": user["username"],
        "exp": datetime.utcnow() + timedelta(hours=10)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}