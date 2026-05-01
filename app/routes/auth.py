from fastapi import APIRouter
from app.core.database import db
from app.auth.utils import create_access_token
from passlib.context import CryptContext

router = APIRouter()

users = db["users"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


@router.post("/register")
def register(data: dict):
    hashed = pwd_context.hash(data["password"])

    users.insert_one({
        "username": data["username"],
        "password": hashed,
        "role": "admin"
    })

    return {"msg": "User created"}


@router.post("/login")
def login(data: dict):
    user = users.find_one({"username": data["username"]})

    if not user or not verify_password(data["password"], user["password"]):
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "admin")
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }