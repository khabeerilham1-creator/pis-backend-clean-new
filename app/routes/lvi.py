from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

cases = db["lab_cases"]
ledger = db["lab_ledger"]
vendors = db["vendors"]

# =========================
# 1. LAB CASE TRACKING
# =========================
@router.post("/case")
def create_case(data: dict):
    data["created_at"] = datetime.utcnow()
    res = cases.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/case")
def get_cases():
    result = []
    for c in cases.find():
        c["_id"] = str(c["_id"])
        result.append(c)
    return result


# =========================
# 2. FINANCIAL LEDGER
# =========================
@router.post("/ledger")
def add_ledger(data: dict):
    data["created_at"] = datetime.utcnow()
    res = ledger.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/ledger")
def get_ledger():
    result = []
    for l in ledger.find():
        l["_id"] = str(l["_id"])
        result.append(l)
    return result


# =========================
# 3. VENDOR MANAGEMENT
# =========================
@router.post("/vendor")
def add_vendor(data: dict):
    res = vendors.insert_one(data)
    return {"id": str(res.inserted_id)}

@router.get("/vendor")
def get_vendors():
    result = []
    for v in vendors.find():
        v["_id"] = str(v["_id"])
        result.append(v)
    return result


# =========================
# DELETE (COMMON)
# =========================
@router.delete("/case/{id}")
def delete_case(id: str):
    cases.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}

@router.delete("/ledger/{id}")
def delete_ledger(id: str):
    ledger.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}

@router.delete("/vendor/{id}")
def delete_vendor(id: str):
    vendors.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}