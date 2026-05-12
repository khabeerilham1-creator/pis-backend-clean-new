from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timedelta

router = APIRouter()

patients = db["patients"]
visits = db["visits"]
afi = db["afi"]
invoice = db["invoices"]


# =========================
# SAFE DATE
# =========================
def parse_date(date_str):

    formats = [

        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y"
    ]

    for f in formats:

        try:

            return datetime.strptime(
                str(date_str),
                f
            )

        except:
            pass

    return None


# =========================
# ALERTS
# =========================
@router.get("/")
def get_alerts():

    alerts = []

    today = datetime.today().date()

    upcoming_limit = (
        today + timedelta(days=7)
    )

    # =========================
    # VISITS
    # =========================
    for v in visits.find():

        visit_date = parse_date(
            v.get("date")
        )

        if not visit_date:
            continue

        visit_day = visit_date.date()

        patient_name = (

            v.get("patient_name")
            or v.get("name")
            or v.get("patient")
            or "Unknown Patient"
        )

        # TODAY
        if visit_day == today:

            alerts.append({

                "title":
                "Today Treatment",

                "message":
                f"📅 {patient_name} has treatment today",

                "priority":
                "high",

                "date":
                str(visit_day)
            })

        # UPCOMING
        elif today < visit_day <= upcoming_limit:

            alerts.append({

                "title":
                "Upcoming Treatment",

                "message":
                f"🗓️ {patient_name} treatment on {visit_day}",

                "priority":
                "low",

                "date":
                str(visit_day)
            })

    # =========================
    # APPOINTMENTS
    # =========================
    for a in afi.find():

        app_date = parse_date(
            a.get("date")
        )

        if not app_date:
            continue

        app_day = app_date.date()

        patient_name = (

            a.get("patient_name")
            or a.get("name")
            or a.get("patient")
            or "Unknown Patient"
        )

        # TODAY
        if app_day == today:

            alerts.append({

                "title":
                "Today Appointment",

                "message":
                f"📅 {patient_name} has appointment today",

                "priority":
                "high",

                "date":
                str(app_day)
            })

        # UPCOMING
        elif today < app_day <= upcoming_limit:

            alerts.append({

                "title":
                "Upcoming Appointment",

                "message":
                f"🗓️ {patient_name} appointment on {app_day}",

                "priority":
                "low",

                "date":
                str(app_day)
            })

    # =========================
    # BIRTHDAYS
    # =========================
    for p in patients.find():

        birth_date = parse_date(
            p.get("birth_date")
        )

        if not birth_date:
            continue

        if (
            birth_date.month == today.month
            and
            birth_date.day == today.day
        ):

            alerts.append({

                "title":
                "Birthday Reminder",

                "message":
                f"🎂 Today is {p.get('name')} birthday",

                "priority":
                "medium",

                "date":
                str(today)
            })

    # =========================
    # PENDING PAYMENTS
    # =========================
    for inv in invoice.find():

        balance = float(
            inv.get("balance", 0)
        )

        if balance > 0:

            alerts.append({

                "title":
                "Pending Payment",

                "message":
                f"💰 Pending payment Rs {balance} for {inv.get('patient_name')}",

                "priority":
                "high",

                "date":
                str(today)
            })

    # =========================
    # SORT
    # =========================
    alerts = sorted(
        alerts,
        key=lambda x: x["date"]
    )

    return alerts