from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

completed_cases = db["completed_cases"]

patients = db["patients"]

invoices = db["invoices"]

checkups = db["checkups"]


# ==========================================
# AUTO TRACKER
# ==========================================
def auto_complete_case(patient_name: str):

    patient = patients.find_one({
        "name": patient_name
    })

    invoice = invoices.find_one({
        "patient_name": patient_name
    })

    if not patient or not invoice:
        return

    balance = float(
        invoice.get("balance", 0)
    )

    tasks_done = True

    patient_checkups = list(
        checkups.find({
            "patient": str(patient["_id"])
        })
    )

    if len(patient_checkups) == 0:
        tasks_done = False

    # ==========================================
    # ONLY COMPLETE WHEN BALANCE CLEARED
    # ==========================================
    if balance <= 0 and tasks_done:

        exists = completed_cases.find_one({
            "patient_name": patient_name
        })

        if exists:
            return

        completed_cases.insert_one({

            "patient_id":
            str(patient["_id"]),

            "patient_name":
            patient_name,

            "mobile_number":
            patient.get(
                "mobile_number",
                ""
            ),

            "address":
            patient.get(
                "address",
                ""
            ),

            "colour_code":
            patient.get(
                "colour_code",
                "friends"
            ),

            "amount":
            invoice.get(
                "amount",
                0
            ),

            "paid":
            invoice.get(
                "paid",
                0
            ),

            "balance":
            invoice.get(
                "balance",
                0
            ),

            "lab_charge":
            invoice.get(
                "lab_charge",
                0
            ),

            "status":
            "Completed",

            "completed_mode":
            "AUTO",

            "completed_at":
            datetime.utcnow()
        })


# ==========================================
# GET ALL
# ==========================================
@router.get("/")
def get_completed_cases():

    # 🔥 AUTO CHECK ALL INVOICES
    all_invoices = list(
        invoices.find()
    )

    for inv in all_invoices:

        auto_complete_case(
            inv.get(
                "patient_name"
            )
        )

    data = []

    for item in completed_cases.find().sort(
        "completed_at",
        -1
    ):

        item["_id"] = str(
            item["_id"]
        )

        data.append(item)

    return data


# ==========================================
# MANUAL COMPLETE
# ==========================================
@router.post("/manual")
def manual_complete(data: dict):

    patient_id = data.get(
        "patient_id"
    )

    patient = patients.find_one({
        "_id": ObjectId(patient_id)
    })

    if not patient:

        return {
            "msg":
            "Patient not found"
        }

    invoice = invoices.find_one({
        "patient_name":
        patient.get("name")
    })

    exists = completed_cases.find_one({
        "patient_id":
        patient_id
    })

    if exists:

        return {
            "msg":
            "Already completed"
        }

    completed_cases.insert_one({

        "patient_id":
        patient_id,

        "patient_name":
        patient.get("name"),

        "mobile_number":
        patient.get(
            "mobile_number",
            ""
        ),

        "address":
        patient.get(
            "address",
            ""
        ),

        "colour_code":
        patient.get(
            "colour_code",
            "friends"
        ),

        "amount":
        invoice.get(
            "amount",
            0
        ) if invoice else 0,

        "paid":
        invoice.get(
            "paid",
            0
        ) if invoice else 0,

        "balance":
        invoice.get(
            "balance",
            0
        ) if invoice else 0,

        "lab_charge":
        invoice.get(
            "lab_charge",
            0
        ) if invoice else 0,

        "status":
        "Completed",

        "completed_mode":
        "MANUAL",

        "completed_at":
        datetime.utcnow()
    })

    return {
        "msg":
        "Case completed manually"
    }


# ==========================================
# REOPEN CASE
# ==========================================
@router.delete("/{id}")
def reopen_case(id: str):

    completed_cases.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg":
        "Case reopened"
    }