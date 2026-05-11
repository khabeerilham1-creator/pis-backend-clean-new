from fastapi import APIRouter, HTTPException
from app.core.database import db
from bson import ObjectId
import hashlib

router = APIRouter()

users = db["users"]


# =========================
# HASH PASSWORD
# =========================
def hash_password(password: str):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =========================
# GET USERS
# =========================
@router.get("/users")
def get_users():

    data = []

    for u in users.find():

        u["_id"] = str(u["_id"])

        # HIDE PASSWORD
        u.pop("password", None)

        data.append(u)

    return data


# =========================
# CREATE USER
# =========================
@router.post("/users")
def create_user(data: dict):

    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    existing = users.find_one({
        "username": username
    })

    if existing:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = {

        "username": username,

        # 🔥 FIXED HASH
        "password": hash_password(password),

        "role": role,

        "permissions": {}
    }

    res = users.insert_one(user)

    user["_id"] = str(
        res.inserted_id
    )

    user.pop("password", None)

    return user


# =========================
# UPDATE USER
# =========================
@router.put("/users/{id}")
def update_user(
    id: str,
    data: dict
):

    update_data = {

        "username":
        data.get("username"),

        "role":
        data.get("role")
    }

    # PASSWORD OPTIONAL
    if data.get("password"):

        update_data["password"] = hash_password(
            data.get("password")
        )

    users.update_one(

        {
            "_id": ObjectId(id)
        },

        {
            "$set": update_data
        }
    )

    return {
        "msg": "User updated ✅"
    }


# =========================
# DELETE USER
# =========================
@router.delete("/users/{id}")
def delete_user(id: str):

    users.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "User deleted ✅"
    }


# =========================
# APPLY PERMISSION
# =========================
@router.post("/apply")
def apply_permission(data: dict):

    username = data.get("username")

    module = data.get("module")

    access = data.get("access")

    users.update_one(

        {
            "username": username
        },

        {
            "$set": {
                f"permissions.{module}": access
            }
        }
    )

    return {
        "msg": "Permission Updated"
    }