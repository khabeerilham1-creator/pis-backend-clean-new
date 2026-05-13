from app.core.database import db
from datetime import datetime
from bson import ObjectId

patient_files = db["patient_files"]
patients = db["patients"]
checkups = db["checkups"]
visits = db["visits"]
billing = db["billing"]
payments = db["payments"]
timeline = db["timeline"]


def sync_patient_file(patient_id: str = None, phone: str = None):

    # =========================
    # 🔥 FIND PATIENT BY PHONE
    # =========================
    if not patient_id and phone:
        patient = patients.find_one({"phone": phone})
        if patient:
            patient_id = str(patient["_id"])

    if not patient_id:
        return

    year = str(datetime.utcnow().year)

    # =========================
    # 🔥 FIX ObjectId
    # =========================
    try:
        patient_obj = ObjectId(patient_id)
    except:
        return

    patient = patients.find_one({"_id": patient_obj})
    if not patient:
        return

    # 🔥 convert _id
    patient["_id"] = str(patient["_id"])

    # =========================
    # 🔥 FIX: HANDLE BOTH STRING + ObjectId
    # =========================
    query = {
        "$or": [
            {"patient_id": patient_id},        # string
            {"patient_id": patient_obj}        # ObjectId
        ]
    }

    data = {
        "patient_info": patient,
        "checkups": list(checkups.find(query, {"_id": 0})),
        "visits": list(visits.find(query, {"_id": 0})),
        "invoices": list(invoices.find(query, {"_id": 0})),
        "payments": list(payments.find(query, {"_id": 0})),
        "timeline": list(timeline.find(query, {"_id": 0}))
    }

    patient_files.update_one(
        {"patient_id": patient_id, "year": year},
        {
            "$set": {
                "patient_id": patient_id,
                "year": year,
                "data": data,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )