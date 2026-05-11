from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.core.database import db

router = APIRouter()

billing_collection = db["billing"]
invoices = db["invoices"]


# =========================
# CREATE BILL
# =========================
@router.post("/billing")
def create_bill(data: dict):

    amount = float(data.get("amount", 0))
    lab_charge = float(data.get("lab_charge", 0))
    discount = float(data.get("discount", 0))
    total = float(data.get("total", amount))

    doctor_share = amount * 0.25
    owner_share = amount - doctor_share - lab_charge

    record = {

        "patient_name": data.get("patient_name"),

        "procedure": data.get("procedure", []),

        "doctor": data.get("doctor"),

        "rows": data.get("rows", []),

        "total": total,

        "discount": discount,

        "amount": amount,

        "final": amount,

        "lab_charge": lab_charge,

        "doctor_share": doctor_share,

        "owner_share": owner_share,

        "created_at": datetime.utcnow()
    }

    billing_collection.insert_one(record)

    # =========================
    # AUTO CREATE INVOICE
    # =========================

    invoice = {

        "patient_name": data.get("patient_name"),

        "rows": data.get("rows", []),

        "payments": [],

        "total": total,

        "discount": discount,

        "amount": amount,

        "final": amount,

        "lab_charge": lab_charge,

        "paid": 0,

        "balance": amount,

        "created_at": datetime.utcnow()
    }

    invoices.insert_one(invoice)

    return {
        "msg": "Saved"
    }


# =========================
# GET ALL
# =========================
@router.get("/billing")
def get_all_bills():

    data = list(
        billing_collection.find().sort(
            "created_at",
            -1
        )
    )

    result = []

    for d in data:

        d["_id"] = str(d["_id"])

        result.append(d)

    return result


# =========================
# GET BY PATIENT
# =========================
@router.get("/billing/{patient_name}")
def get_by_patient(patient_name: str):

    data = list(
        billing_collection.find({
            "patient_name": patient_name
        })
    )

    result = []

    for d in data:

        d["_id"] = str(d["_id"])

        result.append(d)

    return result


# =========================
# UPDATE
# =========================
@router.put("/billing/{id}")
def update_bill(id: str, data: dict):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid ID"
        )

    amount = float(data.get("amount", 0))
    lab_charge = float(data.get("lab_charge", 0))
    discount = float(data.get("discount", 0))
    total = float(data.get("total", amount))

    doctor_share = amount * 0.25

    owner_share = (
        amount
        - doctor_share
        - lab_charge
    )

    billing_collection.update_one(

        {"_id": ObjectId(id)},

        {
            "$set": {

                "procedure":
                data.get("procedure"),

                "doctor":
                data.get("doctor"),

                "rows":
                data.get("rows", []),

                "total":
                total,

                "discount":
                discount,

                "amount":
                amount,

                "final":
                amount,

                "lab_charge":
                lab_charge,

                "doctor_share":
                doctor_share,

                "owner_share":
                owner_share,

                "updated_at":
                datetime.utcnow()
            }
        }
    )

    invoices.update_one(

        {
            "patient_name":
            data.get("patient_name")
        },

        {
            "$set": {

                "rows":
                data.get("rows", []),

                "total":
                total,

                "discount":
                discount,

                "amount":
                amount,

                "final":
                amount,

                "lab_charge":
                lab_charge,

                "balance":
                amount
            }
        }
    )

    return {
        "msg": "Updated"
    }


# =========================
# DELETE
# =========================
@router.delete("/billing/{id}")
def delete_bill(id: str):

    if not ObjectId.is_valid(id):

        raise HTTPException(
            status_code=400,
            detail="Invalid ID"
        )

    billing_collection.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }