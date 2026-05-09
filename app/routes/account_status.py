from fastapi import APIRouter
from app.core.database import db

router = APIRouter()

invoice_collection = db["invoices"]

@router.get("/")
async def get_accounts():

    data = []

    invoices = invoice_collection.find()

    for inv in invoices:

        total = float(
            inv.get("amount", 0)
        )

        paid = float(
            inv.get("paid", 0)
        )

        balance = float(
            inv.get("balance", 0)
        )

        discount = float(
            inv.get("discount", 0)
        )

        lab_charge = float(
            inv.get("lab_charge", 0)
        )

        doctor_share = (
            total - lab_charge
        ) * 0.25

        owner_profit = (
            total -
            doctor_share -
            lab_charge
        )

        data.append({

            "patient_name":
                inv.get(
                    "patient_name",
                    ""
                ),

            "total":
                total,

            "paid":
                paid,

            "balance":
                balance,

            "discount":
                discount,

            "lab_charge":
                lab_charge,

            "doctor_share":
                doctor_share,

            "owner_profit":
                owner_profit
        })

    return data