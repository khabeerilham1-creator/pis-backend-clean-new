from fastapi import APIRouter, HTTPException
from app.core.database import db
from jose import jwt
from datetime import datetime, timedelta
import hashlib

router = APIRouter()

users = db["users"]

SECRET_KEY = "HDC_SUPER_SECRET_2026"
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

        print("🔥 REGISTER HIT:", data)

        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "staff")

        permissions = data.get(
            "permissions",
            {}
        )

        if not username or not password:

            raise HTTPException(
                status_code=400,
                detail="Missing fields"
            )

        existing = users.find_one({
            "username": username
        })

        if existing:

            return {
                "msg": "User already exists"
            }

        users.insert_one({

            "username": username,

            "password":
            hash_password(password),

            "role": role,

            "permissions":
            permissions
        })

        print("✅ USER CREATED")

        return {
            "msg": "User created ✅"
        }

    except Exception as e:

        print("🔥 REGISTER ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: dict):

    try:

        print("\n🔥 LOGIN HIT")

        print("📥 DATA:", data)

        username = data.get("username")
        password = data.get("password")

        print("👤 USERNAME:", username)

        if not username or not password:

            raise HTTPException(
                status_code=400,
                detail="Missing credentials"
            )

        user = users.find_one({
            "username": username
        })

        print("🧾 USER FROM DB:", user)

        if not user:

            raise HTTPException(
                status_code=400,
                detail="User not found"
            )

        hashed_input = hash_password(password)

        print("🔐 INPUT HASH:", hashed_input)

        print("🔐 DB HASH:", user.get("password"))

        db_password = user.get("password")

        if not db_password:

            raise HTTPException(
                status_code=500,
                detail="User password missing"
            )

        if hashed_input != db_password:

            raise HTTPException(
                status_code=400,
                detail="Wrong password"
            )

        # =========================
        # TOKEN
        # =========================
        payload = {

            "sub":
            user["username"],

            "role":
            user.get("role", "staff"),

            "exp":
            datetime.utcnow()
            + timedelta(days=1)
        }

        print("🧪 TOKEN PAYLOAD:", payload)

        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        print("✅ LOGIN SUCCESS")

        return {

            "access_token":
            token,

            "role":
            user.get("role", "staff"),

            "username":
            user.get("username"),

            "permissions":
            user.get("permissions", {})
        }

    except HTTPException:

        raise

    except Exception as e:

        print("🔥 LOGIN ERROR FULL:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================
# DELETE USER
# =========================
@router.delete("/delete-user/{username}")
def delete_user(username: str):

    try:

        users.delete_one({
            "username": username
        })

        print(
            f"🗑️ USER DELETED: {username}"
        )

        return {
            "msg": "User deleted"
        }

    except Exception as e:

        print("🔥 DELETE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================
# UPDATE USER
# =========================
@router.put("/update-user/{username}")
def update_user(username: str, data: dict):

    try:

        update_data = {}

        if data.get("password"):

            update_data["password"] = (
                hash_password(
                    data.get("password")
                )
            )

        if data.get("role"):

            update_data["role"] = (
                data.get("role")
            )

        users.update_one(

            {
                "username": username
            },

            {
                "$set": update_data
            }
        )

        return {
            "msg": "User updated ✅"
        }

    except Exception as e:

        print("🔥 UPDATE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )