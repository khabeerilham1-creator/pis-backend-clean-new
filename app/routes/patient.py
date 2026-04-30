from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.database import db
from bson import ObjectId
import shutil
import os

from app.auth.deps import get_current_user
from app.utils.audit import log_action

router = APIRouter()
patients = db["patients"]

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("🔥 patient router loaded")


# =========================
# GET ALL PATIENTS
# =========================
@router.get("/")
def get_patients(user=Depends(get_current_user)):
    result = []
    for p in patients.find():
        p["_id"] = str(p["_id"])
        result.append(p)
    return result


# =========================
# CREATE PATIENT
# =========================
@router.post("/")
def create_patient(
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),

    # optional fields (match your frontend)
    referral: str = Form(None),
    care_category: str = Form(None),
    conditions: str = Form(None),
    allergies: str = Form(None),
    medications: str = Form(None),
    risk_flags: str = Form(None),
    past_treatments: str = Form(None),
    complaints: str = Form(None),
    habits: str = Form(None),
    signed_forms: str = Form(None),
    estimates: str = Form(None),
    legal_consents: str = Form(None),

    xray: UploadFile = File(None),
    user=Depends(get_current_user)
):
    data = {
        "name": name,
        "age": age,
        "gender": gender,
        "phone": phone,
        "address": address,
        "referral": referral,
        "care_category": care_category,
        "conditions": conditions,
        "allergies": allergies,
        "medications": medications,
        "risk_flags": risk_flags,
        "past_treatments": past_treatments,
        "complaints": complaints,
        "habits": habits,
        "signed_forms": signed_forms,
        "estimates": estimates,
        "legal_consents": legal_consents
    }

    # SAVE XRAY FILE
    if xray:
        file_path = f"{UPLOAD_FOLDER}/{xray.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(xray.file, buffer)
        data["xray"] = file_path

    result = patients.insert_one(data)

    # 🔥 AUDIT LOG
    log_action(user, "create_patient", str(result.inserted_id), data)

    return {"msg": "Patient created"}


# =========================
# UPDATE PATIENT
# =========================
@router.put("/{id}")
def update_patient(
    id: str,
    data: dict,
    user=Depends(get_current_user)
):
    patients.update_one({"_id": ObjectId(id)}, {"$set": data})

    # 🔥 AUDIT LOG
    log_action(user, "update_patient", id, data)

    return {"msg": "Updated"}


# =========================
# DELETE PATIENT
# =========================
@router.delete("/{id}")
def delete_patient(id: str, user=Depends(get_current_user)):
    patients.delete_one({"_id": ObjectId(id)})

    # 🔥 AUDIT LOG
    log_action(user, "delete_patient", id)

    return {"msg": "Deleted"}