from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

from app.modules.timeline import add_to_timeline
from app.modules.file_sync import sync_patient_file
from app.utils.get_patient import get_patient_id_by_phone

router = APIRouter()

checkups = db["checkups"]


# =========================
# GET ALL CHECKUPS
# =========================

@router.get("/")
def get_checkups():

    result = []

    for c in checkups.find():

        c["_id"] = str(c["_id"])

        result.append(c)

    return result


# =========================
# CREATE CHECKUP
# =========================

@router.post("/")
def create_checkup(data: dict):

    print("CHECKUP DATA:", data)

    # 🔥 AUTO LINK PATIENT
    patient_id = data.get("patient_id")

    if not patient_id:

        patient_id = get_patient_id_by_phone(
            data.get("contact")
        )

    # 🔥 SAFETY
    if patient_id:

        data["patient_id"] = str(patient_id)

    else:

        data["patient_id"] = ""

    # 🔥 INSERT
    result = checkups.insert_one(data)

    inserted_id = str(result.inserted_id)

    # 🔥 TIMELINE
    try:

        if data.get("patient_id"):

            add_to_timeline(

                patient_id=data.get("patient_id"),

                event_type="checkup",

                ref_id=inserted_id,

                data={

                    "complaint":
                        data.get("complaint"),

                    "tasks":
                        data.get("tasks", [])

                }

            )

    except Exception as e:

        print("TIMELINE ERROR:", e)

    # 🔥 FILE SYNC
    try:

        sync_patient_file(

            patient_id=data.get("patient_id"),

            phone=data.get("contact")

        )

    except Exception as e:

        print("FILE SYNC ERROR:", e)

    return {

        "msg": "Checkup created",

        "id": inserted_id

    }


# =========================
# UPDATE CHECKUP
# =========================

@router.put("/{id}")
def update_checkup(
    id: str,
    data: dict
):

    if data.get("patient_id"):

        data["patient_id"] = str(
            data.get("patient_id")
        )

    checkups.update_one(

        {"_id": ObjectId(id)},

        {"$set": data}

    )

    try:

        sync_patient_file(

            patient_id=data.get("patient_id"),

            phone=data.get("contact")

        )

    except Exception as e:

        print("SYNC ERROR:", e)

    return {

        "msg": "Updated"

    }


# =========================
# DELETE CHECKUP
# =========================

@router.delete("/{id}")
def delete_checkup(id: str):

    checkups.delete_one({

        "_id": ObjectId(id)

    })

    return {

        "msg": "Deleted"

    }