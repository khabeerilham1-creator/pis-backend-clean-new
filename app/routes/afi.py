from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

appointments = db["appointments"]


@router.get("/")
def get_appointments():
    result = []
    for a in appointments.find():
        a["_id"] = str(a["_id"])
        result.append(a)
    return result


@router.post("/")
def create_appointment(data: dict):
    appointments.insert_one(data)
    return {"msg": "Created"}


@router.put("/{id}")
def update_appointment(id: str, data: dict):
    appointments.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


@router.delete("/{id}")
def delete_appointment(id: str):
    appointments.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}