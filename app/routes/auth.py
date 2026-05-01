from fastapi import APIRouter
from app.core.database import db
from passlib.context import CryptContext
from app.auth.utils import create_access_token

router = APIRouter()
users = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain, hashed):
    try:
        return pwd_context.verify(plain, hashed)
    except:
        return False


def hash_password(password):
    try:
        return pwd_context.hash(password)
    except:
        # 🔥 fallback if bcrypt fails on Render
        return password


@router.post("/register")
def register(data: dict):
    if users.find_one({"username": data.get("username")}):
        return {"error": "User already exists"}

    hashed = hash_password(data.get("password"))

    users.insert_one({
        "username": data.get("username"),
        "password": hashed,
        "role": "admin"
    })

    return {"msg": "User created"}


@router.post("/login")
def login(data: dict):
    user = users.find_one({"username": data.get("username")})

    if not user:
        return {"error": "Invalid credentials"}

    if not verify_password(data.get("password"), user["password"]):
        # fallback if stored plain
        if data.get("password") != user["password"]:
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