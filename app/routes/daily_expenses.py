from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db

router = APIRouter(prefix="/daily-expenses", tags=["daily-expenses"])

VALID_CATEGORIES = {
    "refreshment",
    "food",
    "tea",
    "kitchen",
    "general",
    "washroom",
}


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(record_id: str) -> ObjectId:
    try:
        return ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid daily expense ID.")


def current_period() -> tuple[int, int]:
    now = datetime.utcnow()
    return now.month, now.year


def clean_record(data: dict) -> dict:
    record = dict(data or {})
    record.pop("_id", None)

    category = str(record.get("category") or "general").strip().lower()
    record["category"] = category if category in VALID_CATEGORIES else "general"
    record["description"] = str(record.get("description") or "").strip()
    record["qty"] = float(record.get("qty") or 0)
    record["amount"] = float(record.get("amount") or 0)
    record["date"] = str(record.get("date") or datetime.utcnow().date().isoformat())

    month, year = current_period()
    record["periodMonth"] = int(record.get("periodMonth") or month)
    record["periodYear"] = int(record.get("periodYear") or year)

    return record


@router.get("/")
async def get_daily_expenses(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    category: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=2000),
):
    default_month, default_year = current_period()
    query = {
        "periodMonth": month or default_month,
        "periodYear": year or default_year,
    }

    if category and category != "all":
        clean_category = category.strip().lower()
        if clean_category in VALID_CATEGORIES:
            query["category"] = clean_category

    records = list(
        db.daily_expenses.find(query)
        .sort([("category", 1), ("date", -1), ("createdAt", -1)])
        .limit(limit)
    )

    return {"expenses": [fix_id(record) for record in records]}


@router.post("/", status_code=201)
async def create_daily_expense(expense: dict):
    data = clean_record(expense)
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    if not data["description"]:
        raise HTTPException(status_code=400, detail="Description is required.")

    try:
        result = db.daily_expenses.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Daily expense save failed. {exc}")

    data["_id"] = str(result.inserted_id)
    return {"message": "Daily expense saved.", "expense": data}


@router.put("/{expense_id}")
async def update_daily_expense(expense_id: str, expense: dict):
    oid = valid_object_id(expense_id)
    data = clean_record(expense)
    data["updatedAt"] = datetime.utcnow().isoformat()

    result = db.daily_expenses.update_one({"_id": oid}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Daily expense not found.")

    saved = db.daily_expenses.find_one({"_id": oid})
    return {"message": "Daily expense updated.", "expense": fix_id(saved)}


@router.delete("/{expense_id}")
async def delete_daily_expense(expense_id: str):
    oid = valid_object_id(expense_id)
    result = db.daily_expenses.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Daily expense not found.")

    return {"message": "Daily expense deleted."}
