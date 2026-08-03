from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db

router = APIRouter(prefix="/entry-sheet", tags=["entry-sheet"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(entry_id: str) -> ObjectId:
    try:
        return ObjectId(entry_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid entry sheet ID.")


def clean_entry(data: dict) -> dict:
    entry = dict(data or {})
    entry.pop("_id", None)

    for field in [
        "date",
        "name",
        "time",
        "purpose",
        "contact",
        "entryTime",
        "exitTime",
        "shiftId",
        "shiftName",
        "createdByRole",
        "createdByName",
    ]:
        entry[field] = str(entry.get(field) or "").strip()

    if not entry["date"]:
        entry["date"] = datetime.utcnow().date().isoformat()

    if not entry["name"]:
        raise HTTPException(status_code=400, detail="Name is required.")

    return entry


@router.get("/")
async def get_entry_sheet_rows(
    shift: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=2000),
):
    query = {}

    if shift and shift != "all":
        query["shiftId"] = str(shift).strip()

    if date:
        query["date"] = str(date).strip()

    rows = list(
        db.entry_sheet.find(query)
        .sort([("date", -1), ("time", -1), ("createdAt", -1)])
        .limit(limit)
    )

    return {"entries": [fix_id(row) for row in rows]}


@router.post("/", status_code=201)
async def create_entry_sheet_row(entry: dict):
    data = clean_entry(entry)
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    try:
        result = db.entry_sheet.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Entry sheet save failed. {exc}")

    data["_id"] = str(result.inserted_id)
    return {"message": "Entry saved.", "entry": data}


@router.put("/{entry_id}")
async def update_entry_sheet_row(entry_id: str, entry: dict):
    oid = valid_object_id(entry_id)
    data = clean_entry(entry)
    data["updatedAt"] = datetime.utcnow().isoformat()

    result = db.entry_sheet.update_one({"_id": oid}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entry sheet row not found.")

    saved = db.entry_sheet.find_one({"_id": oid})
    return {"message": "Entry updated.", "entry": fix_id(saved)}


@router.delete("/{entry_id}")
async def delete_entry_sheet_row(entry_id: str):
    oid = valid_object_id(entry_id)
    result = db.entry_sheet.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry sheet row not found.")

    return {"message": "Entry deleted."}
