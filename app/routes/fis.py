from fastapi import APIRouter
from app.models.fis_model import billing_collection, payments_collection
from app.schemas.fis_schema import BillingCreate, PaymentCreate, DiscountCreate
from datetime import datetime

router = APIRouter()

# =========================
# 1. BILLING ENGINE
# =========================
@router.post("/billing")
def create_bill(data: BillingCreate):

    record = data.dict()

    record["created_at"] = datetime.utcnow()
    record["discount"] = 0
    record["paid"] = 0
    record["balance"] = data.amount

    billing_collection.insert_one(record)

    return {"message": "Billing added successfully"}


@router.get("/billing/{patient_name}")
def get_bills(patient_name: str):
    return list(billing_collection.find({"patient_name": patient_name}, {"_id": 0}))


# =========================
# 2. DISCOUNT GOVERNANCE
# =========================
@router.post("/discount")
def apply_discount(data: DiscountCreate):

    bills = list(billing_collection.find({"patient_name": data.patient_name}))

    for bill in bills:
        new_balance = max(
            bill.get("amount", 0)
            - bill.get("paid", 0)
            - data.discount,
            0
        )

        billing_collection.update_one(
            {"_id": bill["_id"]},
            {
                "$set": {
                    "discount": data.discount,
                    "approved_by": data.approved_by,
                    "balance": new_balance
                }
            }
        )

    return {"message": "Discount applied successfully"}


# =========================
# 3. PAYMENT TRACKING (INSTALLMENTS)
# =========================
@router.post("/payment")
def add_payment(data: PaymentCreate):

    # Save payment
    payments_collection.insert_one({
        "patient_name": data.patient_name,
        "amount": data.amount,
        "method": data.method,
        "note": data.note,
        "date": datetime.utcnow()
    })

    # Update billing
    bills = list(billing_collection.find({"patient_name": data.patient_name}))

    for bill in bills:
        new_paid = bill.get("paid", 0) + data.amount

        new_balance = max(
            bill.get("amount", 0)
            - new_paid
            - bill.get("discount", 0),
            0
        )

        billing_collection.update_one(
            {"_id": bill["_id"]},
            {
                "$set": {
                    "paid": new_paid,
                    "balance": new_balance
                }
            }
        )

    return {"message": "Payment recorded successfully"}


@router.get("/payments/{patient_name}")
def get_payments(patient_name: str):
    return list(payments_collection.find({"patient_name": patient_name}, {"_id": 0}))


# =========================
# 4. BALANCE SYSTEM (NEW)
# =========================
@router.get("/balance/{patient_name}")
def get_balance(patient_name: str):

    bills = list(billing_collection.find({"patient_name": patient_name}))

    total = sum([b.get("amount", 0) for b in bills])
    paid = sum([b.get("paid", 0) for b in bills])
    discount = sum([b.get("discount", 0) for b in bills])

    balance = total - paid - discount

    return {
        "total": total,
        "paid": paid,
        "discount": discount,
        "balance": balance
    }


# =========================
# 5. REVENUE ALLOCATION
# =========================
@router.get("/revenue/{patient_name}")
def revenue_split(patient_name: str):

    bills = list(billing_collection.find({"patient_name": patient_name}))
    total = sum([b.get("amount", 0) for b in bills])

    return {
        "total": total,
        "doctor_share": total * 0.4,
        "lab_share": total * 0.2,
        "expense_pool": total * 0.2,
        "owner": total * 0.2
    }


# =========================
# 6. ANALYTICS
# =========================
@router.get("/analytics/daily")
def daily_revenue():

    bills = list(billing_collection.find())
    total = sum([b.get("amount", 0) for b in bills])

    return {"daily_revenue": total}


@router.get("/analytics/monthly")
def monthly_revenue():

    bills = list(billing_collection.find())
    total = sum([b.get("amount", 0) for b in bills])

    return {"monthly_revenue": total}