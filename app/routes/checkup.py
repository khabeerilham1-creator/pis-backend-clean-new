from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

checkups = db["checkups"]


# =========================
# GET ALL CHECKUPS
# =========================
@router.get("/")
def get_checkups():
    result = []
    for c in checkups.find():
        c["_id"] = str(c["_id"])
        result.append(c)
    return result


# =========================
# CREATE CHECKUP
# =========================
@router.post("/")
def create_checkup(data: dict):
    checkups.insert_one(data)
    return {"msg": "Checkup created"}


# =========================
# UPDATE CHECKUP
# =========================
@router.put("/{id}")
def update_checkup(id: str, data: dict):
    checkups.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


# =========================
# DELETE CHECKUP
# =========================
@router.delete("/{id}")
def delete_checkup(id: str):
    checkups.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}