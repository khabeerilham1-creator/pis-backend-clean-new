from fastapi import APIRouter, Form, UploadFile, File
from app.core.database import db
from bson import ObjectId
from pymongo import ReturnDocument
import os
import shutil

router = APIRouter(prefix="/api")  # ✅ IMPORTANT

patients = db["patients"]
counter = db["counters"]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 🔥 GET NEXT NUMBER
def get_next_patient_no():
    c = counter.find_one_and_update(
        {"_id": "patient_no"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return c["seq"]


# ================= CREATE =================
@router.post("/patients")
async def create_patient(
    name: str = Form(...),
    age: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    xray: UploadFile = File(None)
):

    patient_no = get_next_patient_no()

    file_path = None
    if xray:
        file_path = f"{UPLOAD_DIR}/{xray.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(xray.file, buffer)

    patient = {
        "patient_no": patient_no,
        "name": name,
        "age": age,
        "phone": phone,
        "address": address,
        "xray": file_path
    }

    res = patients.insert_one(patient)
    return {"id": str(res.inserted_id), "patient_no": patient_no}


# ================= GET =================
@router.get("/patients")
def get_patients():
    data = []
    for p in patients.find():
        p["_id"] = str(p["_id"])
        data.append(p)
    return data


# ================= UPDATE =================
@router.put("/patients/{id}")
async def update_patient(
    id: str,
    name: str = Form(...),
    age: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
):

    patients.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": name,
            "age": age,
            "phone": phone,
            "address": address
        }}
    )

    return {"message": "Updated"}


# ================= DELETE =================
@router.delete("/patients/{id}")
def delete_patient(id: str):
    patients.delete_one({"_id": ObjectId(id)})
    return {"message": "Deleted"}