from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db
from app.models.inventory import InventoryItem

router = APIRouter(prefix="/inventory", tags=["inventory"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(item_id: str) -> ObjectId:
    try:
        return ObjectId(item_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid inventory item ID.")


def item_to_dict(item: InventoryItem) -> dict:
    if hasattr(item, "model_dump"):
        return item.model_dump()

    return item.dict()


@router.get("/")
async def get_inventory(
    search: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
    sort: str = Query("date"),
    order: int = Query(-1),
):
    query = {}

    if search and search.strip():
        query["productName"] = {"$regex": search.strip(), "$options": "i"}

    items = list(db.inventory.find(query).sort(sort, order).limit(limit))

    return {"items": [fix_id(item) for item in items]}


@router.post("/", status_code=201)
async def create_inventory_item(item: InventoryItem):
    data = item_to_dict(item)
    now = datetime.utcnow().isoformat()

    data["productName"] = data.get("productName", "").strip()
    data["qty"] = float(data.get("qty") or 0)
    data["minQty"] = float(data.get("minQty") or 0)
    data["date"] = data.get("date") or now[:10]
    data["createdAt"] = now
    data["updatedAt"] = now

    if not data["productName"]:
        raise HTTPException(status_code=400, detail="Product name is required.")

    try:
        result = db.inventory.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Inventory save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Inventory item saved.", "item": data}


@router.put("/{item_id}")
async def update_inventory_item(item_id: str, item: dict):
    oid = valid_object_id(item_id)
    item.pop("_id", None)

    if "qty" in item:
        item["qty"] = float(item.get("qty") or 0)
    if "minQty" in item:
        item["minQty"] = float(item.get("minQty") or 0)

    item["updatedAt"] = datetime.utcnow().isoformat()

    result = db.inventory.update_one({"_id": oid}, {"$set": item})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Inventory item not found.")

    return {"message": "Inventory item updated.", "modified": result.modified_count}


@router.delete("/{item_id}")
async def delete_inventory_item(item_id: str):
    oid = valid_object_id(item_id)
    result = db.inventory.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Inventory item not found.")

    return {"message": "Inventory item deleted."}
