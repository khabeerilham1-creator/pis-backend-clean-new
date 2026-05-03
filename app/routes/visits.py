from fastapi import APIRouter, Depends
from app.core.database import db
from app.auth.deps import get_current_user
from datetime import datetime

from app.modules.timeline import add_to_timeline
from app.modules.file_sync import sync_patient_file
from app.utils.get_patient import get_patient_id_by_phone

router = APIRouter()
visits = db["visits"]


@router.post("/")
def create_visit(data: dict, user=Depends(get_current_user)):

    # ✅ AUTO LINK BY PHONE
    if not data.get("patient_id"):
        data["patient_id"] = get_patient_id_by_phone(data.get("phone"))

    data["patient_id"] = str(data.get("patient_id"))
    data["created_at"] = datetime.utcnow()

    res = visits.insert_one(data)

    add_to_timeline(
        patient_id=data.get("patient_id"),
        event_type="visit",
        ref_id=str(res.inserted_id),
        data={
            "reason": data.get("reason")
        }
    )

    sync_patient_file(
        patient_id=data.get("patient_id"),
        phone=data.get("phone")
    )

    return {"msg": "Visit created"}


@router.get("/")
def get_visits(user=Depends(get_current_user)):
    result = []
    for v in visits.find():
        v["_id"] = str(v["_id"])
        result.append(v)
    return result