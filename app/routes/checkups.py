from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

from app.modules.timeline import add_to_timeline
from app.modules.file_sync import sync_patient_file
from app.utils.get_patient import get_patient_id_by_phone

router = APIRouter()

checkups = db["checkups"]


@router.get("/")
def get_checkups():
    result = []
    for c in checkups.find():
        c["_id"] = str(c["_id"])
        result.append(c)
    return result


@router.post("/")
def create_checkup(data: dict):

    # ✅ AUTO LINK BY PHONE
    if not data.get("patient_id"):
        data["patient_id"] = get_patient_id_by_phone(data.get("phone"))

    # 🔥 FORCE STRING
    data["patient_id"] = str(data.get("patient_id"))

    result = checkups.insert_one(data)

    add_to_timeline(
        patient_id=data.get("patient_id"),
        event_type="checkup",
        ref_id=str(result.inserted_id),
        data={
            "notes": data.get("notes"),
            "diagnosis": data.get("diagnosis")
        }
    )

    # 🔥 MAIN FIX
    sync_patient_file(
        patient_id=data.get("patient_id"),
        phone=data.get("phone")
    )

    return {"msg": "Checkup created"}


@router.put("/{id}")
def update_checkup(id: str, data: dict):

    data["patient_id"] = str(data.get("patient_id"))

    checkups.update_one({"_id": ObjectId(id)}, {"$set": data})

    sync_patient_file(patient_id=data.get("patient_id"))

    return {"msg": "Updated"}


@router.delete("/{id}")
def delete_checkup(id: str):
    checkups.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}