from fastapi import APIRouter, Depends
from app.core.database import db
from app.auth.deps import get_current_user
from datetime import datetime
from bson import ObjectId

from app.modules.timeline import add_to_timeline
from app.modules.file_sync import sync_patient_file
from app.utils.get_patient import get_patient_id_by_phone

router = APIRouter()
visits = db["visits"]


# =========================
# CREATE VISIT
# =========================
@router.post("/")
def create_visit(data: dict, user=Depends(get_current_user)):

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
            "diagnosis": data.get("diagnosis"),
            "treatment": data.get("treatment")
        }
    )

    sync_patient_file(patient_id=data.get("patient_id"))

    return {"msg": "Visit created"}


# =========================
# GET VISITS
# =========================
@router.get("/")
def get_visits(user=Depends(get_current_user)):
    result = []
    for v in visits.find():
        v["_id"] = str(v["_id"])
        result.append(v)
    return result


# =========================
# UPDATE VISIT 🔥 (THIS FIXES YOUR ERROR)
# =========================
@router.put("/{id}")
def update_visit(id: str, data: dict):

    if not ObjectId.is_valid(id):
        return {"msg": "Invalid ID"}

    data["patient_id"] = str(data.get("patient_id"))

    visits.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )

    # 🔥 update patient file
    sync_patient_file(patient_id=data.get("patient_id"))

    return {"msg": "Updated"}


# =========================
# DELETE VISIT 🔥
# =========================
@router.delete("/{id}")
def delete_visit(id: str):

    if not ObjectId.is_valid(id):
        return {"msg": "Invalid ID"}

    visits.delete_one({"_id": ObjectId(id)})

    return {"msg": "Deleted"}