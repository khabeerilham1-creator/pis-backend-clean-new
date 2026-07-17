from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db

router = APIRouter(prefix="/account-payables", tags=["account-payables"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(record_id: str) -> ObjectId:
    try:
        return ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid account payable ID.")


def current_period() -> tuple[int, int]:
    now = datetime.utcnow()
    return now.month, now.year


def clean_record(data: dict) -> dict:
    record = dict(data or {})
    record.pop("_id", None)

    record["to"] = str(record.get("to") or "").strip()
    record["description"] = str(record.get("description") or "").strip()
    record["amount"] = float(record.get("amount") or 0)
    record["status"] = str(record.get("status") or "Un paid").strip() or "Un paid"
    record["date"] = str(record.get("date") or datetime.utcnow().date().isoformat())

    month, year = current_period()
    record["periodMonth"] = int(record.get("periodMonth") or month)
    record["periodYear"] = int(record.get("periodYear") or year)

    return record


@router.get("/")
async def get_account_payables(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    limit: int = Query(1000, ge=1, le=2000),
):
    default_month, default_year = current_period()
    query = {
        "periodMonth": month or default_month,
        "periodYear": year or default_year,
    }

    records = list(
        db.account_payables.find(query)
        .sort([("date", -1), ("createdAt", -1)])
        .limit(limit)
    )

    return {"payables": [fix_id(record) for record in records]}


@router.post("/", status_code=201)
async def create_account_payable(payable: dict):
    data = clean_record(payable)
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    if not data["to"]:
        raise HTTPException(status_code=400, detail="Payee name is required.")

    try:
        result = db.account_payables.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Account payable save failed. {exc}")

    data["_id"] = str(result.inserted_id)
    return {"message": "Account payable saved.", "payable": data}


@router.put("/{payable_id}")
async def update_account_payable(payable_id: str, payable: dict):
    oid = valid_object_id(payable_id)
    data = clean_record(payable)
    data["updatedAt"] = datetime.utcnow().isoformat()

    result = db.account_payables.update_one({"_id": oid}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Account payable not found.")

    saved = db.account_payables.find_one({"_id": oid})
    return {"message": "Account payable updated.", "payable": fix_id(saved)}


@router.delete("/{payable_id}")
async def delete_account_payable(payable_id: str):
    oid = valid_object_id(payable_id)
    result = db.account_payables.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account payable not found.")

    return {"message": "Account payable deleted."}
