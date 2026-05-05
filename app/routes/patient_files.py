from fastapi import APIRouter
from app.core.database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

patient_files = db["patient_files"]
patients = db["patients"]
checkups = db["checkups"]
visits = db["visits"]
billing = db["billing"]
payments = db["payments"]
timeline = db["timeline"]
invoices = db["invoices"]   # ✅ ADDED


# =========================
# BUILD / UPDATE FILE
# =========================
@router.get("/build/{patient_id}")
def build_patient_file(patient_id: str):

    year = str(datetime.utcnow().year)

    try:
        patient = patients.find_one({"_id": ObjectId(patient_id)})
    except:
        patient = None

    if not patient:
        return {"msg": "Patient not found"}

    patient["_id"] = str(patient["_id"])

    query = {
        "$or": [
            {"patient_id": patient_id},
            {"patient": patient_id}
        ]
    }

    data = {
        "patient_info": patient,
        "checkups": list(checkups.find({"patient": patient_id})),
        "visits": list(visits.find({"patient": patient_id})),
        "billing": list(billing.find({"patient_name": patient.get("name")})),
        "payments": list(payments.find({"patient_name": patient.get("name")})),
        "timeline": list(timeline.find({"patient_id": patient_id})),
        "invoices": list(invoices.find({"patient_id": patient_id}))   # ✅ ADDED
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

    return {"msg": "Patient file created/updated"}


# =========================
# GET SINGLE PATIENT FILE (FIXED FOR FRONTEND)
# =========================
@router.get("/{patient_id}")
def get_patient_file_simple(patient_id: str):

    year = str(datetime.utcnow().year)

    try:
        patient_obj = ObjectId(patient_id)
    except:
        patient_obj = None

    file = patient_files.find_one({
        "year": year,
        "$or": [
            {"patient_id": patient_id},
            {"patient_id": patient_obj}
        ]
    })

    if not file:
        return {"msg": "Not found"}

    data = file.get("data", {})

    # 🔥 NORMALIZED RESPONSE (FRONTEND FRIENDLY)
    return {
        "patient": data.get("patient_info", {}),
        "patient_id": patient_id,
        "checkups": data.get("checkups", []),
        "visits": data.get("visits", []),
        "invoices": data.get("invoices", []),
        "timeline": data.get("timeline", [])
    }


# =========================
# SEARCH
# =========================
@router.get("/search/{query}")
def search_files(query: str):

    result = []

    for f in patient_files.find():
        info = f.get("data", {}).get("patient_info", {})

        name = str(info.get("name", "")).lower()
        phone = str(info.get("phone", ""))

        if query.lower() in name or query in phone:
            f["_id"] = str(f["_id"])
            result.append(f)

    return result