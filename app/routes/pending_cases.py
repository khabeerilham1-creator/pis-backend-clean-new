from fastapi import APIRouter
from app.core.database import db

router = APIRouter()

invoices = db["invoices"]
patients = db["patients"]


# =========================
# GET PENDING CASES
# =========================
@router.get("/")
def get_pending_cases():

    result = []

    data = invoices.find({
        "balance": {
            "$gt": 0
        }
    })

    for item in data:

        patient = patients.find_one({
            "name": item.get("patient_name")
        })

        result.append({

            "_id": str(item["_id"]),

            "patient_name":
            item.get("patient_name", ""),

            "amount":
            item.get("amount", 0),

            "paid":
            item.get("paid", 0),

            "balance":
            item.get("balance", 0),

            "lab_charge":
            item.get("lab_charge", 0),

            "mobile_number":
            patient.get("mobile_number", "")
            if patient else "",

            "address":
            patient.get("address", "")
            if patient else "",

            "colour_code":
            patient.get("colour_code", "green")
            if patient else "green"
        })

    return result