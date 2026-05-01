from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

lvi_collection = db["lvi"]

# =========================
# GET ALL
# =========================
@router.get("/")
def get_lvi():
    data = []
    for i in lvi_collection.find():
        i["_id"] = str(i["_id"])
        data.append(i)
    return data   # ✅ MUST BE LIST


# =========================
# CREATE
# =========================
@router.post("/")
def create_lvi(data: dict):
    res = lvi_collection.insert_one(data)
    return {"id": str(res.inserted_id)}


# =========================
# DELETE
# =========================
@router.delete("/{id}")
def delete_lvi(id: str):
    lvi_collection.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}