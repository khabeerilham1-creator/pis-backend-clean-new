from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

creditors = db["creditors"]

@router.post("/")
def add(data: dict):
    data["created_at"] = datetime.utcnow()
    res = creditors.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/")
def get():
    data = []
    for c in creditors.find():
        c["_id"] = str(c["_id"])
        data.append(c)
    return data

@router.delete("/{id}")
def delete(id: str):
    creditors.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}