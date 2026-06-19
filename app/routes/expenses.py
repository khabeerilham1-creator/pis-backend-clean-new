from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db
from app.models.expense import Expense

router = APIRouter(prefix="/expenses", tags=["expenses"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(expense_id: str) -> ObjectId:
    try:
        return ObjectId(expense_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid expense ID.")


def expense_to_dict(expense: Expense) -> dict:
    if hasattr(expense, "model_dump"):
        return expense.model_dump()

    return expense.dict()


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
        query["expenseName"] = {"$regex": search.strip(), "$options": "i"}

    expenses = list(db.expenses.find(query).sort(sort, order).limit(limit))

    return {"expenses": [fix_id(expense) for expense in expenses]}


@router.post("/", status_code=201)
async def create_expense(expense: Expense):
    data = expense_to_dict(expense)
    now = datetime.utcnow().isoformat()

    data["category"] = data.get("category") if data.get("category") in ["clinical", "home"] else "clinical"
    data["expenseName"] = data.get("expenseName", "").strip()
    data["status"] = data.get("status") if data.get("status") in ["paid", "unpaid"] else "paid"
    data["amount"] = float(data.get("amount") or 0)
    data["date"] = data.get("date") or now[:10]
    data["createdAt"] = now
    data["updatedAt"] = now

    if not data["expenseName"]:
        raise HTTPException(status_code=400, detail="Expense name is required.")

    try:
        result = db.expenses.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Expense save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Expense saved.", "expense": data}


@router.put("/{expense_id}")
async def update_expense(expense_id: str, expense: dict):
    oid = valid_object_id(expense_id)
    expense.pop("_id", None)

    if "category" in expense and expense["category"] not in ["clinical", "home"]:
        expense["category"] = "clinical"
    if "status" in expense and expense["status"] not in ["paid", "unpaid"]:
        expense["status"] = "paid"
    if "amount" in expense:
        expense["amount"] = float(expense.get("amount") or 0)

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
