from fastapi import APIRouter, Depends
from app.core.database import db
from datetime import datetime
from app.dependencies import get_current_user

router = APIRouter()

cis_collection = db["cis"]

@router.post("/")
async def create_cis(data: dict, user=Depends(get_current_user)):

    doc = {
        "patient_id": data.get("patient_id"),
        "diagnosis": data.get("diagnosis"),
        "treatment": data.get("treatment"),
        "notes": data.get("notes"),

        # NEW STRUCTURE
        "treatment_plan": data.get("treatment_plan", []),
        "procedure_notes": data.get("procedure_notes", []),
        "followups": data.get("followups", []),
        "images": data.get("images", []),

        "created_by": user.get("sub"),
        "role": user.get("role"),
        "created_at": datetime.utcnow()
    }

    cis_collection.insert_one(doc)

    return {"msg": "CIS Saved"}