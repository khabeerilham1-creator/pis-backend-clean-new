from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

users = db["users"]

# =========================
# GET USERS
# =========================
@router.get("/users")
def get_users():

    data = []

    for u in users.find():

        u["_id"] = str(u["_id"])

        data.append(u)

    return data


# =========================
# CREATE USER
# =========================
@router.post("/users")
def create_user(data: dict):

    user = {
        "username": data.get("username"),
        "password": data.get("password"),
        "role": data.get("role"),
        "permissions": {}
    }

    res = users.insert_one(user)

    user["_id"] = str(res.inserted_id)

    return user


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