from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

pending_cases = db["pending_cases"]
billing = db["billing"]
patients = db["patients"]


# =========================
# AUTO TRACK PENDING
# =========================
@router.get("/")
def get_pending_cases():

    auto_cases = []

    bills = list(billing.find())

    for b in bills:

        balance = float(
            b.get("balance", 0)
        )

        # ONLY PENDING
        if balance > 0:

            patient = patients.find_one({
                "name": b.get("patient_name")
            })

            auto_cases.append({

                "_id":
                str(b["_id"]),

                "patient_name":
                b.get("patient_name"),

                "mobile_number":
                patient.get(
                    "mobile_number",
                    ""
                ) if patient else "",

                "address":
                patient.get(
                    "address",
                    ""
                ) if patient else "",

                "amount":
                b.get("amount", 0),

                "paid":
                b.get("paid", 0),

                "balance":
                balance,

                "lab_charge":
                b.get("lab_charge", 0),

                "source":
                "auto",

                "created_at":
                b.get("created_at")
            })

    manual_cases = []

    for m in pending_cases.find():

        m["_id"] = str(m["_id"])

        m["source"] = "manual"

        manual_cases.append(m)

    return auto_cases + manual_cases


# =========================
# MANUAL ADD
# =========================
@router.post("/")
def add_pending_case(data: dict):

    item = {

        "patient_name":
        data.get("patient_name"),

        "mobile_number":
        data.get("mobile_number"),

        "address":
        data.get("address"),

        "amount":
        data.get("amount", 0),

        "paid":
        data.get("paid", 0),

        "balance":
        data.get("balance", 0),

        "lab_charge":
        data.get("lab_charge", 0),

        "created_at":
        datetime.utcnow()
    }

    result = pending_cases.insert_one(item)

    item["_id"] = str(
        result.inserted_id
    )

    return item


# =========================
# DELETE MANUAL
# =========================
@router.delete("/{id}")
def delete_pending_case(id: str):

    pending_cases.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }