from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db
router = APIRouter(prefix="/expenses", tags=["expenses"])

VALID_CATEGORIES = {
    "administration",
    "team",
    "dental-material",
    "dental-implants",
    "clinical",
    "home",
}


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(expense_id: str) -> ObjectId:
    try:
        return ObjectId(expense_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid expense ID.")


def clean_expense(data: dict) -> dict:
    expense = dict(data or {})
    expense.pop("_id", None)

    category = expense.get("category") or "administration"
    expense["category"] = category if category in VALID_CATEGORIES else "administration"

    for number_field in [
        "amount",
        "paid",
        "basicSalary",
        "allocation",
        "deduction",
        "netSalary",
        "qty",
        "ratePerUnit",
        "ratePerImplant",
        "totalAmount",
    ]:
        if number_field in expense:
            expense[number_field] = float(expense.get(number_field) or 0)

    if "payments" in expense:
        expense["payments"] = [
            {
                **payment,
                "amount": float(payment.get("amount") or 0),
            }
            for payment in expense.get("payments", [])
            if isinstance(payment, dict)
        ]

    if not expense.get("date") and not expense.get("dueDate") and not expense.get("joiningDate"):
        expense["date"] = datetime.utcnow().date().isoformat()

    return expense


@router.get("/")
async def get_expenses(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
    sort: str = Query("date"),
    order: int = Query(-1),
):
    query = {}

    if category and category != "all":
        query["category"] = category

    if search and search.strip():
        s = search.strip()
        query["$or"] = [
            {"expenseName": {"$regex": s, "$options": "i"}},
            {"description": {"$regex": s, "$options": "i"}},
            {"name": {"$regex": s, "$options": "i"}},
            {"shop": {"$regex": s, "$options": "i"}},
            {"vendor": {"$regex": s, "$options": "i"}},
            {"item": {"$regex": s, "$options": "i"}},
            {"items": {"$regex": s, "$options": "i"}},
        ]

    expenses = list(db.expenses.find(query).sort(sort, order).limit(limit))

    return {"expenses": [fix_id(expense) for expense in expenses]}


@router.post("/", status_code=201)
async def create_expense(expense: dict):
    data = clean_expense(expense)
    now = datetime.utcnow().isoformat()

    data["expenseName"] = str(data.get("expenseName") or data.get("description") or "").strip()
    data["status"] = data.get("status") or "unpaid"
    data["createdAt"] = now
    data["updatedAt"] = now

    if not data["expenseName"] and not data.get("name") and not data.get("item") and not data.get("items"):
        raise HTTPException(status_code=400, detail="Expense description is required.")

    try:
        result = db.expenses.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Expense save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Expense saved.", "expense": data}


@router.put("/{expense_id}")
async def update_expense(expense_id: str, expense: dict):
    oid = valid_object_id(expense_id)
    expense = clean_expense(expense)

    expense["updatedAt"] = datetime.utcnow().isoformat()

    result = db.expenses.update_one({"_id": oid}, {"$set": expense})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found.")

    return {"message": "Expense updated.", "modified": result.modified_count}


@router.delete("/{expense_id}")
async def delete_expense(expense_id: str):
    oid = valid_object_id(expense_id)
    result = db.expenses.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found.")

    return {"message": "Expense deleted."}
