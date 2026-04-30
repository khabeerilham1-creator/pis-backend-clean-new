from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

cis = db["cis"]


@router.post("/")
def create_cis(data: dict):
    cis.insert_one(data)
    return {"msg": "Created"}


@router.get("/")
def get_cis():
    result = []
    for c in cis.find():
        c["_id"] = str(c["_id"])
        result.append(c)
    return result


@router.put("/{id}")
def update_cis(id: str, data: dict):
    cis.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


@router.delete("/{id}")
def delete_cis(id: str):
    cis.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}