from fastapi import APIRouter, Depends
from app.core.database import db
from app.auth.deps import get_current_user
from datetime import datetime

router = APIRouter()

visits = db["visits"]


@router.post("/")
def create_visit(data: dict, user=Depends(get_current_user)):
    data["created_at"] = datetime.utcnow()
    visits.insert_one(data)
    return {"msg": "Visit created"}


@router.get("/")
def get_visits(user=Depends(get_current_user)):
    result = []
    for v in visits.find():
        v["_id"] = str(v["_id"])
        result.append(v)
    return result