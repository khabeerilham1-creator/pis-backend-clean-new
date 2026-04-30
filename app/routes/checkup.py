from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

checkups = db["checkups"]

@router.post("/checkups")
def create_checkup(data: dict):
    result = checkups.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/checkups")
def get_checkups():
    data = []
    for c in checkups.find():
        c["_id"] = str(c["_id"])
        data.append(c)
    return data

@router.put("/checkups/{id}")
def update_checkup(id: str, data: dict):
    checkups.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "updated"}

@router.delete("/checkups/{id}")
def delete_checkup(id: str):
    checkups.delete_one({"_id": ObjectId(id)})
    return {"msg": "deleted"}