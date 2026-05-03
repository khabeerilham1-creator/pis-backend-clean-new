from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

router = APIRouter()
timeline = db["timeline"]


def add_to_timeline(patient_id: str, event_type: str, ref_id=None, data=None):
    timeline.insert_one({
        "patient_id": str(patient_id),
        "event_type": event_type,
        "ref_id": ref_id,
        "data": data or {},
        "created_at": datetime.utcnow()
    })


@router.get("/{patient_id}")
def get_timeline(patient_id: str):
    data = list(
        timeline.find({"patient_id": str(patient_id)}).sort("created_at", -1)
    )

    for d in data:
        d["_id"] = str(d["_id"])

    return data