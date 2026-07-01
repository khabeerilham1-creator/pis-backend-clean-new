from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Query

from app.core.database import db

router = APIRouter(prefix="/activity-logs", tags=["activity-logs"])


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/")
async def get_activity_logs(
    limit: int = Query(300, ge=1, le=1000),
    role: Optional[str] = Query(None),
):
    query = {}

    if role and role != "all":
        query["role"] = role

    logs = list(db.activity_logs.find(query).sort("timestamp", -1).limit(limit))

    return {"logs": [fix_id(log) for log in logs]}


@router.post("/", status_code=201)
async def create_activity_log(entry: dict):
    log = dict(entry or {})
    log.pop("_id", None)
    log["actor"] = str(log.get("actor") or "Unknown")
    log["role"] = str(log.get("role") or "staff")
    log["action"] = str(log.get("action") or "Activity")
    log["target"] = str(log.get("target") or "")
    log["details"] = log.get("details") or {}
    log["timestamp"] = log.get("timestamp") or datetime.utcnow().isoformat()

    result = db.activity_logs.insert_one(log)
    log["_id"] = str(result.inserted_id) if isinstance(result.inserted_id, ObjectId) else result.inserted_id

    return {"message": "Activity log saved.", "log": log}
