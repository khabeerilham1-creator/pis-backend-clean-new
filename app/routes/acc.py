from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

router = APIRouter()

invoices = db["invoices"]
visits = db["visits"]
bills = db["bills"]
debtors = db["debtors"]
creditors = db["creditors"]


def safe_date(obj):
    try:
        if hasattr(obj, "strftime"):
            return obj.strftime("%Y-%m-%d"), obj.month
    except:
        pass
    return None, None


@router.get("/revenue")
def revenue():

    today = datetime.utcnow().strftime("%Y-%m-%d")

    daily = 0
    monthly = 0

    for i in invoices.find():

        created = i.get("created_at")
        date_str, month = safe_date(created)

        if not date_str:
            continue

        amount = float(i.get("amount", 0))

        if date_str == today:
            daily += amount

        if month == datetime.utcnow().month:
            monthly += amount

    return {
        "daily": daily,
        "monthly": monthly
    }


@router.get("/doctors")
def doctor_stats():

    result = {}

    for i in invoices.find():

        for r in i.get("rows", []):

            doc = r.get("doctor")

            if not doc:
                continue

            if doc not in result:
                result[doc] = {
                    "cases": 0,
                    "revenue": 0
                }

            result[doc]["cases"] += 1
            result[doc]["revenue"] += float(r.get("rate", 0))

    return result


@router.get("/conversion")
def conversion():

    consults = visits.count_documents({})
    treatments = invoices.count_documents({})

    percent = (treatments / consults * 100) if consults else 0

    return {"conversion": percent}


@router.get("/finance")
def finance():

    revenue = 0
    for i in invoices.find():
        revenue += float(i.get("amount", 0))

    expenses = sum(float(b.get("amount", 0)) for b in bills.find())
    debt_total = sum(float(d.get("amount", 0)) for d in debtors.find())
    credit_total = sum(float(c.get("amount", 0)) for c in creditors.find())

    profit = revenue - expenses

    alerts = []

    if expenses > revenue:
        alerts.append("⚠️ Expenses exceed revenue")

    if debt_total > 50000:
        alerts.append("⚠️ High debtors")

    if profit < 0:
        alerts.append("⚠️ Clinic running in loss")

    return {
        "revenue": revenue,
        "expenses": expenses,
        "profit": profit,
        "debtors": debt_total,
        "creditors": credit_total,
        "alerts": alerts
    }


# 🔥 DRILL DOWN
@router.get("/doctor/{name}")
def doctor_detail(name: str):

    cases = []
    total = 0

    for i in invoices.find():
        for r in i.get("rows", []):
            if r.get("doctor") == name:
                cases.append(r)
                total += float(r.get("rate", 0))

    return {
        "doctor": name,
        "cases": cases,
        "revenue": total
    }