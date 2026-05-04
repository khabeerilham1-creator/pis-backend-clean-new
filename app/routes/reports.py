from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
billing = db["billing"]
visits = db["visits"]


# =========================
# GET FULL PATIENT REPORT
# =========================
@router.get("/report/{query}")
def get_report(query: str):

    patient = None

    # 🔥 1. TRY OBJECT ID
    if ObjectId.is_valid(query):
        patient = patients.find_one({"_id": ObjectId(query)})

    # 🔥 2. TRY NAME
    if not patient:
        patient = patients.find_one({"name": query})

    # 🔥 3. TRY PHONE
    if not patient:
        patient = patients.find_one({"phone": query})

    if not patient:
        return {"error": "Patient not found"}

    patient_id = str(patient["_id"])

    # =========================
    # FETCH RELATED DATA
    # =========================
    patient_checkups = list(checkups.find({"patient": patient_id}))
    patient_visits = list(visits.find({"patient": patient_id}))
    patient_bills = list(billing.find({"patient_name": patient.get("name")}))

    # =========================
    # CLEAN OBJECT IDs
    # =========================
    def clean(data):
        for d in data:
            d["_id"] = str(d["_id"])
        return data

    return {
        "patient": {
            "_id": patient_id,
            "name": patient.get("name"),
            "phone": patient.get("phone")
        },
        "checkups": clean(patient_checkups),
        "visits": clean(patient_visits),
        "billing": clean(patient_bills)
    }