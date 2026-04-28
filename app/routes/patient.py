from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import shutil
import os
from uuid import uuid4

router = APIRouter()

# ✅ TEMP STORAGE (replace later with MongoDB)
patients_db = []

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔥 GET ALL
@router.get("/patients")
def get_patients():
    return patients_db


# 🔥 CREATE
@router.post("/patients")
def create_patient(
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),

    referral: str = Form(""),
    care_category: str = Form(""),

    conditions: str = Form(""),
    allergies: str = Form(""),
    medications: str = Form(""),
    risk_flags: str = Form(""),

    past_treatments: str = Form(""),
    complaints: str = Form(""),
    habits: str = Form(""),

    signed_forms: str = Form(""),
    estimates: str = Form(""),
    legal_consents: str = Form(""),

    xray: Optional[UploadFile] = File(None)
):
    patient = {
        "_id": str(uuid4()),
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
        "legal_consents": legal_consents,
        "xray": ""
    }

    # ✅ FILE UPLOAD
    if xray:
        filename = f"{uuid4()}_{xray.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(xray.file, buffer)

        patient["xray"] = file_path

    patients_db.append(patient)

    return {"msg": "Patient created", "id": patient["_id"]}


# 🔥 UPDATE
@router.put("/patients/{id}")
def update_patient(
    id: str,
    name: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    xray: Optional[UploadFile] = File(None)
):
    for p in patients_db:
        if p["_id"] == id:
            p["name"] = name
            p["age"] = age
            p["gender"] = gender
            p["phone"] = phone
            p["address"] = address

            if xray:
                filename = f"{uuid4()}_{xray.filename}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(xray.file, buffer)

                p["xray"] = file_path

            return {"msg": "Updated"}

    return {"error": "Not found"}


# 🔥 DELETE
@router.delete("/patients/{id}")
def delete_patient(id: str):
    global patients_db
    patients_db = [p for p in patients_db if p["_id"] != id]
    return {"msg": "Deleted"}