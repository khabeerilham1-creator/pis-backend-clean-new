from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()
appointments = db["appointments"]

@router.post("/appointments")
async def create(data: dict):

    data["created_at"] = datetime.now()
    appointments.insert_one(data)
    return {"msg": "Saved"}


@router.get("/appointments")
def get():
    data = []
    for a in appointments.find():
        a["_id"] = str(a["_id"])
        data.append(a)
    return data


@router.put("/appointments/{id}")
async def update(id: str, data: dict):
    appointments.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


@router.delete("/appointments/{id}")
def delete(id: str):
    appointments.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}