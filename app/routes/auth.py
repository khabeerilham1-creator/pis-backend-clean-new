from fastapi import APIRouter, HTTPException
from app.core.database import db
from passlib.context import CryptContext
from app.auth.utils import hash_password, verify_password, create_access_token

router = APIRouter()

users = db["users"]


@router.post("/register")
def register(data: dict):
    if users.find_one({"username": data["username"]}):
        raise HTTPException(status_code=400, detail="User exists")

    data["password"] = hash_password(data["password"])

    # default role if not sent
    if "role" not in data:
        data["role"] = "staff"

    users.insert_one(data)

    return {"msg": "User created"}


@router.post("/login")
def login(data: dict):
    user = users.find_one({"username": data["username"]})

    if not user or not verify_password(data["password"], user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "role": user["role"]
    }