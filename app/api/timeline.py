from fastapi import APIRouter
from app.core.database import db

router = APIRouter()
timeline = db["timeline"]

@router.get("/{patient_id}")
def get_patient_timeline(patient_id: str):
    data = list(timeline.find({"patient_id": patient_id}).sort("created_at", -1))
    
    for item in data:
        item["_id"] = str(item["_id"])
    
    return data