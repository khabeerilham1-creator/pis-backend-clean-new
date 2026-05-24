from fastapi import APIRouter
from bson import ObjectId

from app.models.patient import Patient
from app.core.database import db

router = APIRouter()


# CREATE PATIENT
@router.post("/patients")
async def create_patient(
    patient: Patient
):

    patient_dict = patient.dict()

    result = db.patients.insert_one(
        patient_dict
    )

    return {
        "message":
        "Patient Saved Successfully",

        "id":
        str(result.inserted_id)
    }


# GET ALL PATIENTS
@router.get("/patients")
async def get_patients():

    patients = list(
        db.patients.find()
    )

    for patient in patients:

        patient["_id"] = str(
            patient["_id"]
        )

    return patients


# DELETE PATIENT
@router.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: str
):

    result = db.patients.delete_one({
        "_id": ObjectId(patient_id)
    })

    return {
        "message":
        "Patient Deleted Successfully"
    }