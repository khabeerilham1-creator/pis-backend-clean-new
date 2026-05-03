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


# =========================
# BUILD / UPDATE FILE (GET for browser)
# =========================
@router.get("/build/{patient_id}")
def build_patient_file(patient_id: str):

    year = str(datetime.utcnow().year)

    # 🔥 SAFE FIND (ObjectId + string support)
    patient = None

    try:
        patient = patients.find_one({"_id": ObjectId(patient_id)})
    except:
        pass

    if not patient:
        patient = patients.find_one({"_id": patient_id})

    if not patient:
        return {"msg": "Patient not found"}

    # 🔥 FORCE STRING ID
    patient_id = str(patient["_id"])

    # collect all data
    data = {
        "patient_info": patient,
        "checkups": list(checkups.find({"patient_id": patient_id}, {"_id": 0})),
        "visits": list(visits.find({"patient_id": patient_id}, {"_id": 0})),
        "billing": list(billing.find({"patient_id": patient_id}, {"_id": 0})),
        "payments": list(payments.find({"patient_id": patient_id}, {"_id": 0})),
        "timeline": list(timeline.find({"patient_id": patient_id}, {"_id": 0}))
    }

    # remove Mongo _id
    data["patient_info"].pop("_id", None)

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
# GET FILES BY YEAR
# =========================
@router.get("/{year}")
def get_files_by_year(year: str):

    result = []
    for f in patient_files.find({"year": str(year)}):
        f["_id"] = str(f["_id"])
        result.append(f)

    return result


# =========================
# GET SINGLE PATIENT FILE
# =========================
@router.get("/file/{patient_id}/{year}")
def get_patient_file(patient_id: str, year: str):

    file = patient_files.find_one({
        "patient_id": str(patient_id),
        "year": str(year)
    })

    if not file:
        return {"msg": "Not found"}

    file["_id"] = str(file["_id"])
    return file


# =========================
# SEARCH (NAME / PHONE)
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


# =========================
# MANUAL ADD FILE
# =========================
@router.post("/manual")
def manual_file(data: dict):

    year = str(datetime.utcnow().year)

    patient_files.insert_one({
        "patient_id": str(data.get("patient_id")),
        "year": year,
        "data": data,
        "created_at": datetime.utcnow()
    })

    return {"msg": "Manual file added"}