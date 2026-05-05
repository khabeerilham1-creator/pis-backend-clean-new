from fastapi import APIRouter
from app.core.database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

staff = db["staff"]
attendance = db["attendance"]
evaluation = db["evaluation"]

# =========================
# STAFF
# =========================
@router.post("/staff")
def add_staff(data: dict):
    data["created_at"] = datetime.utcnow()
    res = staff.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/staff")
def get_staff():
    data = []
    for s in staff.find():
        s["_id"] = str(s["_id"])
        data.append(s)
    return data

@router.delete("/staff/{id}")
def delete_staff(id: str):
    staff.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}


# =========================
# ATTENDANCE
# =========================
@router.post("/attendance")
def mark_attendance(data: dict):
    data["date"] = datetime.utcnow()
    res = attendance.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/attendance")
def get_attendance():
    data = []
    for a in attendance.find():
        a["_id"] = str(a["_id"])
        data.append(a)
    return data


# =========================
# EVALUATION
# =========================
@router.post("/evaluation")
def add_eval(data: dict):
    data["date"] = datetime.utcnow()
    res = evaluation.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/evaluation")
def get_eval():
    data = []
    for e in evaluation.find():
        e["_id"] = str(e["_id"])
        data.append(e)
    return data