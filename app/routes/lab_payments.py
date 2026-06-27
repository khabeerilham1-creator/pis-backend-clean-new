from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db

router = APIRouter(prefix="/lab-payments", tags=["lab-payments"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(payment_id: str) -> ObjectId:
    try:
        return ObjectId(payment_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid lab payment ID.")


def clean_payment(payment: dict) -> dict:
    data = dict(payment or {})
    data.pop("_id", None)
    data["labName"] = str(data.get("labName") or "Lab").strip()
    data["date"] = str(data.get("date") or datetime.utcnow().date().isoformat())
    data["amount"] = float(data.get("amount") or 0)
    data["method"] = str(data.get("method") or "")
    data["note"] = str(data.get("note") or "")
    return data


@router.get("/")
async def get_lab_payments(
    lab_name: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=2000),
):
    query = {}

    if lab_name and lab_name != "all":
        query["labName"] = lab_name

    payments = list(
        db.lab_payments.find(query)
        .sort("date", -1)
        .limit(limit)
    )

    return {"payments": [fix_id(payment) for payment in payments]}


@router.post("/", status_code=201)
async def create_lab_payment(payment: dict):
    data = clean_payment(payment)
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    if data["amount"] <= 0:
        raise HTTPException(status_code=400, detail="Paid amount is required.")

    try:
        result = db.lab_payments.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Lab payment save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Lab payment saved.", "payment": data}


@router.put("/{payment_id}")
async def update_lab_payment(payment_id: str, payment: dict):
    oid = valid_object_id(payment_id)
    data = clean_payment(payment)
    data["updatedAt"] = datetime.utcnow().isoformat()

    result = db.lab_payments.update_one({"_id": oid}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lab payment not found.")

    saved = db.lab_payments.find_one({"_id": oid})

    return {"message": "Lab payment updated.", "payment": fix_id(saved)}


@router.delete("/{payment_id}")
async def delete_lab_payment(payment_id: str):
    oid = valid_object_id(payment_id)
    result = db.lab_payments.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lab payment not found.")

    return {"message": "Lab payment deleted."}
