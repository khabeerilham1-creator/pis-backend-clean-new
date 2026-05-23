from fastapi import APIRouter
from app.models.patient import Patient
from app.core.database import db

router = APIRouter()


@router.post("/patients")
async def create_patient(patient: Patient):

    patient_dict = patient.dict()

    result = db.patients.insert_one(patient_dict)

    return {
        "message": "Patient Saved Successfully",
        "id": str(result.inserted_id)
    }


@router.get("/patients")
async def get_patients():

    patients = list(db.patients.find())

    for patient in patients:
        patient["_id"] = str(patient["_id"])

    return patients