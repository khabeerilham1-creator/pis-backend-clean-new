from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

bills = db["bills"]

@router.post("/")
def add_bill(data: dict):
    data["created_at"] = datetime.utcnow()
    res = bills.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/")
def get_bills():
    data = []
    for b in bills.find():
        b["_id"] = str(b["_id"])
        data.append(b)
    return data

@router.delete("/{id}")
def delete_bill(id: str):
    bills.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}