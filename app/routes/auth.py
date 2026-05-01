from fastapi import APIRouter
from app.core.database import db
from passlib.context import CryptContext
from app.auth.utils import create_access_token

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
    user = users.find_one({"username": data.get("username")})

    if not user:
        return {"error": "Invalid credentials"}

    try:
        if not verify_password(data.get("password"), user["password"]):
            return {"error": "Invalid credentials"}
    except:
        return {"error": "Password error"}

    token = create_access_token({
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "admin")
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }