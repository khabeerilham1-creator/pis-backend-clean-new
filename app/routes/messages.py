from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db
from app.models.message import Message

router = APIRouter(prefix="/messages", tags=["messages"])

VALID_ROLES = {"admin", "receptionist", "dentist", "doctor"}


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])

    return doc


def valid_object_id(message_id: str) -> ObjectId:
    try:
        return ObjectId(message_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid message ID.")


def message_to_dict(message: Message) -> dict:
    if hasattr(message, "model_dump"):
        return message.model_dump()

    return message.dict()


def clean_role(value: str) -> str:
    role = str(value or "").strip().lower()
    return role if role in VALID_ROLES else ""


def clean_message(data: dict) -> dict:
    message = dict(data or {})
    message.pop("_id", None)
    message["fromRole"] = clean_role(message.get("fromRole"))
    message["toRole"] = clean_role(message.get("toRole"))
    message["fromName"] = str(message.get("fromName") or "").strip()
    message["toName"] = str(message.get("toName") or "").strip()
    message["body"] = str(message.get("body") or "").strip()
    message["read"] = bool(message.get("read") or False)

    if not isinstance(message.get("metadata"), dict):
        message["metadata"] = {}

    if not message["fromRole"]:
        raise HTTPException(status_code=400, detail="Sender role is required.")
    if not message["toRole"]:
        raise HTTPException(status_code=400, detail="Recipient role is required.")
    if not message["body"]:
        raise HTTPException(status_code=400, detail="Message text is required.")

    return message


@router.get("/")
async def get_messages(
    role: Optional[str] = Query(None),
    unreadOnly: bool = Query(False),
    limit: int = Query(200, ge=1, le=1000),
):
    clean_current_role = clean_role(role or "")
    query = {}

    if clean_current_role and clean_current_role != "admin":
        query = {"$or": [{"fromRole": clean_current_role}, {"toRole": clean_current_role}]}

    if unreadOnly and clean_current_role:
        unread_query = {"toRole": clean_current_role, "read": {"$ne": True}}
        query = {"$and": [query, unread_query]} if query else unread_query

    messages = list(db.messages.find(query).sort("createdAt", -1).limit(limit))

    return {"messages": [fix_id(message) for message in messages]}


@router.post("/", status_code=201)
async def create_message(message: Message):
    data = clean_message(message_to_dict(message))
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    try:
        result = db.messages.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Message save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Message sent.", "chatMessage": data}


@router.patch("/{message_id}/read")
async def mark_message_read(message_id: str):
    oid = valid_object_id(message_id)
    result = db.messages.update_one(
        {"_id": oid},
        {"$set": {"read": True, "readAt": datetime.utcnow().isoformat()}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Message not found.")

    return {"message": "Message marked as read."}


@router.delete("/{message_id}")
async def delete_message(message_id: str):
    oid = valid_object_id(message_id)
    result = db.messages.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found.")

    return {"message": "Message deleted."}
