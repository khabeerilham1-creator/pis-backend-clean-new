from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timedelta

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
billing = db["billing"]
payments = db["payments"]


# =========================
# MAIN DASHBOARD
# =========================
@router.get("/")
def dashboard():

    total_patients = patients.count_documents({})
    total_checkups = checkups.count_documents({})

    total_revenue = sum([p.get("amount", 0) for p in payments.find()])
    total_billing = sum([b.get("amount", 0) for b in billing.find()])

    return {
        "total_patients": total_patients,
        "total_checkups": total_checkups,
        "total_revenue": total_revenue,
        "total_billing": total_billing
    }


# =========================
# DAILY STATS
# =========================
@router.get("/daily")
def daily_stats():

    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)

    daily_patients = patients.count_documents({
        "created_at": {"$gte": start, "$lt": end}
    })

    daily_checkups = checkups.count_documents({
        "created_at": {"$gte": start, "$lt": end}
    })

    daily_revenue = sum([
        p.get("amount", 0)
        for p in payments.find({
            "date": {"$gte": start, "$lt": end}
        })
    ])

    return {
        "daily_patients": daily_patients,
        "daily_checkups": daily_checkups,
        "daily_revenue": daily_revenue
    }


# =========================
# MONTHLY STATS
# =========================
@router.get("/monthly")
def monthly_stats():

    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)

    if now.month == 12:
        end = datetime(now.year + 1, 1, 1)
    else:
        end = datetime(now.year, now.month + 1, 1)

    monthly_revenue = sum([
        p.get("amount", 0)
        for p in payments.find({
            "date": {"$gte": start, "$lt": end}
        })
    ])

    monthly_checkups = checkups.count_documents({
        "created_at": {"$gte": start, "$lt": end}
    })

    return {
        "monthly_revenue": monthly_revenue,
        "monthly_checkups": monthly_checkups
    }


# =========================
# GROWTH (LAST 7 DAYS)
# =========================
@router.get("/growth")
def growth():

    data = []

    for i in range(7):
        day = datetime.utcnow().date() - timedelta(days=i)
        start = datetime(day.year, day.month, day.day)
        end = start + timedelta(days=1)

        count = checkups.count_documents({
            "created_at": {"$gte": start, "$lt": end}
        })

        data.append({
            "date": str(day),
            "checkups": count
        })

    return list(reversed(data))