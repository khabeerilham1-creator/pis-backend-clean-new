from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db

router = APIRouter(prefix="/dentist-revenue", tags=["dentist-revenue"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(record_id: str) -> ObjectId:
    try:
        return ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid revenue record ID.")


def clean_record(record: dict) -> dict:
    data = dict(record or {})
    data.pop("_id", None)

    data["dentistName"] = str(data.get("dentistName") or "Dentist 1").strip() or "Dentist 1"
    data["doctorName"] = str(data.get("doctorName") or data["dentistName"]).strip()
    data["patientId"] = str(data.get("patientId") or "")
    data["patientName"] = str(data.get("patientName") or "")
    data["expenses"] = [item for item in data.get("expenses", []) if isinstance(item, dict)]
    data["sessions"] = [item for item in data.get("sessions", []) if isinstance(item, dict)]
    data["patientTotal"] = float(data.get("patientTotal") or 0)
    data["patientPaid"] = float(data.get("patientPaid") or 0)
    data["patientBalance"] = float(data.get("patientBalance") or 0)
    data["totalAmount"] = float(data.get("totalAmount") or 0)
    data["expenseTotal"] = float(data.get("expenseTotal") or 0)
    data["remainingAmount"] = float(data.get("remainingAmount") or 0)
    data["share25"] = float(data.get("share25") or 0)

    return data


@router.get("/")
async def get_revenue_records(
    dentist: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
):
    query = {}

    if dentist and dentist != "all":
        query["dentistName"] = dentist

    if patient_id:
        query["patientId"] = patient_id

    records = list(
        db.dentist_revenue.find(query)
        .sort("updatedAt", -1)
        .limit(limit)
    )

    return {"records": [fix_id(record) for record in records]}


@router.post("/", status_code=201)
async def create_revenue_record(record: dict):
    data = clean_record(record)
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    try:
        result = db.dentist_revenue.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Dentist revenue save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Dentist revenue saved.", "record": data}


@router.put("/{record_id}")
async def update_revenue_record(record_id: str, record: dict):
    oid = valid_object_id(record_id)
    data = clean_record(record)
    data["updatedAt"] = datetime.utcnow().isoformat()

    result = db.dentist_revenue.update_one({"_id": oid}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dentist revenue record not found.")

    saved = db.dentist_revenue.find_one({"_id": oid})

    return {"message": "Dentist revenue updated.", "record": fix_id(saved)}


@router.delete("/{record_id}")
async def delete_revenue_record(record_id: str):
    oid = valid_object_id(record_id)
    result = db.dentist_revenue.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dentist revenue record not found.")

    return {"message": "Dentist revenue deleted."}
