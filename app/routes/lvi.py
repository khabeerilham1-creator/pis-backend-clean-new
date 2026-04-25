from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()
lvi_collection = db["lvi"]

@router.post("/lvi")
async def create_lvi(data: dict):

    payable = float(data.get("lab_payable", 0) or 0)
    paid = float(data.get("paid", 0) or 0)

    record = {
        "case_entry": data.get("case_entry"),
        "lab_assignment": data.get("lab_assignment"),
        "deadline": data.get("deadline"),

        "lab_payable": payable,
        "paid": paid,
        "pending": payable - paid,

        "supplier": data.get("supplier"),
        "material": data.get("material"),
        "equipment": data.get("equipment"),

        "created_at": datetime.now()
    }

    res = lvi_collection.insert_one(record)
    return {"id": str(res.inserted_id)}


@router.get("/lvi")
def get_lvi():
    data = []
    for r in lvi_collection.find().sort("created_at", -1):
        r["_id"] = str(r["_id"])
        data.append(r)
    return data


@router.put("/lvi/{id}")
async def update_lvi(id: str, data: dict):
    lvi_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


@router.delete("/lvi/{id}")
def delete_lvi(id: str):
    lvi_collection.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}