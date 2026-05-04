from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timedelta

router = APIRouter()

billing = db["billing"]
patients = db["patients"]
checkups = db["checkups"]


# =========================
# MAIN DASHBOARD
# =========================
@router.get("/")
def dashboard():

    total_patients = patients.count_documents({})
    total_checkups = checkups.count_documents({})

    bills = list(billing.find())

    total_revenue = sum([
        float(b.get("amount", 0))
        for b in bills
    ])

    total_lab = sum([
        float(b.get("lab_charge", 0))
        for b in bills
    ])

    doctor = total_revenue * 0.25
    owner = total_revenue - doctor - total_lab

    return {
        "patients": total_patients,
        "checkups": total_checkups,
        "revenue": total_revenue,

        "split": {
            "doctor": round(doctor, 2),
            "lab": round(total_lab, 2),
            "owner": round(owner, 2)
        }
    }


# =========================
# DAILY (THIS WAS MISSING → 404)
# =========================
@router.get("/daily")
def daily():

    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)

    daily_patients = patients.count_documents({
        "created_at": {"$gte": start, "$lt": end}
    })

    bills = list(billing.find({
        "created_at": {"$gte": start, "$lt": end}
    }))

    daily_revenue = sum([
        float(b.get("amount", 0))
        for b in bills
    ])

    return {
        "today_patients": daily_patients,
        "today_revenue": daily_revenue
    }