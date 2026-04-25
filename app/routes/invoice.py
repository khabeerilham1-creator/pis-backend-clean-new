from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()
invoices = db["invoices"]

@router.post("/invoice")
async def create_invoice(data: dict):

    qty = float(data.get("qty", 0))
    rate = float(data.get("rate", 0))

    total = qty * rate

    p1 = float(data.get("payment1", 0))
    p2 = float(data.get("payment2", 0))

    invoice = {
        "patient": data.get("patient"),  # patient_no
        "procedure": data.get("procedure"),
        "qty": qty,
        "rate": rate,
        "total": total,
        "paid": p1 + p2,
        "balance": total - (p1 + p2),
        "created_at": datetime.now()
    }

    res = invoices.insert_one(invoice)
    return {"id": str(res.inserted_id)}


@router.get("/invoices")
def get():
    data = []
    for i in invoices.find():
        i["_id"] = str(i["_id"])
        data.append(i)
    return data


@router.put("/invoice/{id}")
async def update(id: str, data: dict):
    invoices.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


@router.delete("/invoice/{id}")
def delete(id: str):
    invoices.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}