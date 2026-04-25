from fastapi import APIRouter
from app.core.database import db

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
invoices = db["invoices"]
appointments = db["appointments"]
cis = db["cis"]
lvi = db["lvi"]


@router.get("/dashboard/{patient_no}")
def get_dashboard(patient_no: int):

    patient = patients.find_one({"patient_no": patient_no})

    if not patient:
        return {"error": "Patient not found"}

    return {
        "patient": patient,
        "checkups": list(checkups.find({"patient": patient_no})),
        "invoices": list(invoices.find({"patient": patient_no})),
        "appointments": list(appointments.find({"patient": patient_no})),
        "cis": list(cis.find({"patient_id": str(patient["_id"])})),
        "lvi": list(lvi.find({}))
    }