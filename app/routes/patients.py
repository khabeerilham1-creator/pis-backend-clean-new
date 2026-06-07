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

    # TOTAL PATIENTS
    total_patients = (
        db.patients.count_documents({})
    )

    # AUTO REG NO
    new_reg_no = str(
        total_patients + 1
    ).zfill(5)

    # SAVE INSIDE BIOGRAPHY
    if "biography" not in patient_dict:

        patient_dict["biography"] = {}

    patient_dict["biography"][
        "regNo"
    ] = new_reg_no

    # INSERT
    result = db.patients.insert_one(
        patient_dict
    )

    return {

        "message":
        "Patient Saved Successfully",

        "id":
        str(result.inserted_id),

        "reg_no":
        new_reg_no

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


# UPDATE PATIENT
@router.put("/patients/{patient_id}")
async def update_patient(
    patient_id: str,
    patient: dict
):

    db.patients.update_one(
        {
            "_id": ObjectId(patient_id)
        },
        {
            "$set": patient
        }
    )

    return {
        "message":
        "Patient Updated Successfully"
    }


# DELETE PATIENT
@router.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: str
):

    db.patients.delete_one({
        "_id": ObjectId(patient_id)
    })

    return {
        "message":
        "Patient Deleted Successfully"
    }