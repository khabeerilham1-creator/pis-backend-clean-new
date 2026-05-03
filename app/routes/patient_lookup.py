from app.core.database import db
from bson import ObjectId

patients = db["patients"]

def get_patient_id_by_phone(phone: str):

    if not phone:
        return None

    patient = patients.find_one({"phone": phone})

    if not patient:
        return None

    return str(patient["_id"])