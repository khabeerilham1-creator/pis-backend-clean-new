from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
invoices = db["invoices"]

# =========================
# MAIN DASHBOARD
# =========================
@router.get("/")
def dashboard():

    today = datetime.utcnow().date()

    total_patients = patients.count_documents({})
    total_checkups = checkups.count_documents({})

    total_revenue = 0
    today_revenue = 0

    doctor_share = 0
    lab_total = 0
    owner_profit = 0

    for i in invoices.find():

        amount = float(i.get("amount", 0))
        total_revenue += amount

        # 🔥 DATE FIX
        created = i.get("created_at")
        if created and created.date() == today:
            today_revenue += amount

        # 🔥 SPLIT FIX (BASED ON YOUR SYSTEM)
        lab = float(i.get("lab_charge", 0))
        doc = amount * 0.25
        owner = amount - doc - lab

        doctor_share += doc
        lab_total += lab
        owner_profit += owner

    return {
        "patients": total_patients,
        "checkups": total_checkups,
        "revenue": total_revenue,

        # 🔥 FIXED
        "today_patients": 0,  # optional (you can improve later)
        "today_revenue": today_revenue,

        "split": {
            "doctor": doctor_share,
            "lab": lab_total,
            "owner": owner_profit
        }
    }


# =========================
# DAILY ENDPOINT (OPTIONAL)
# =========================
@router.get("/daily")
def daily():

    today = datetime.utcnow().date()

    today_revenue = 0

    for i in invoices.find():
        created = i.get("created_at")

        if created and created.date() == today:
            today_revenue += float(i.get("amount", 0))

    return {
        "today_revenue": today_revenue
    }