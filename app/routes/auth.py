from fastapi import APIRouter, HTTPException
from app.core.database import users_collection

router = APIRouter(prefix="/auth")

@router.post("/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({
        "$or": [
            {"username": username},
            {"email": username}
        ]
    })

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if str(password).strip() != str(user.get("password", "")).strip():
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Not approved")

    return {
        "access_token": "dummy_token",
        "user": user.get("username") or user.get("email")
    }