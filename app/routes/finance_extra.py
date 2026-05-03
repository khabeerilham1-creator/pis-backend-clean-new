from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

from app.modules.timeline import add_to_timeline

router = APIRouter()

debtors = db["debtors"]
creditors = db["creditors"]


# =========================
# DEBTORS (PATIENTS OWE YOU)
# =========================
@router.post("/debt")
def add_debt(data: dict):

    record = {
        "patient_id": data.get("patient_id"),
        "patient_name": data.get("patient_name"),
        "amount": data.get("amount", 0),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    res = debtors.insert_one(record)

    # timeline log
    add_to_timeline(
        patient_id=data.get("patient_id"),
        event_type="debt",
        ref_id=str(res.inserted_id),
        data={
            "amount": data.get("amount")
        }
    )

    return {"msg": "Debt added"}


@router.get("/debtors")
def get_debtors():
    result = []
    for d in debtors.find():
        d["_id"] = str(d["_id"])
        result.append(d)
    return result


# =========================
# CREDITORS (YOU OWE MONEY)
# =========================
@router.post("/credit")
def add_credit(data: dict):

    record = {
        "vendor": data.get("vendor"),
        "amount": data.get("amount", 0),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    res = creditors.insert_one(record)

    return {"msg": "Credit added"}


@router.get("/creditors")
def get_creditors():
    result = []
    for c in creditors.find():
        c["_id"] = str(c["_id"])
        result.append(c)
    return result