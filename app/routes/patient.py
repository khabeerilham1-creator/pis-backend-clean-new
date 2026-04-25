from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

patients = db["patients"]
counter = db["counters"]


# 🔥 GET NEXT NUMBER
def get_next_patient_no():
    c = counter.find_one_and_update(
        {"_id": "patient_no"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return c["seq"]


# ================= CREATE =================
@router.post("/patients")
async def create_patient(data: dict):

    patient_no = get_next_patient_no()

    patient = {
        "patient_no": patient_no,  # 🔥 SHORT ID
        "name": data.get("name"),
        "age": data.get("age"),
        "phone": data.get("phone"),
        "address": data.get("address")
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