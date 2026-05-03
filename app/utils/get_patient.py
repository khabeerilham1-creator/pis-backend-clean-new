from app.core.database import db

patients = db["patients"]

def get_patient_id_by_phone(phone):
    if not phone:
        return None

    p = patients.find_one({"phone": phone})

    if p:
        return str(p["_id"])

    return None