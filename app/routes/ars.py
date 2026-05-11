from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

router = APIRouter()

patients = db["patients"]
visits = db["visits"]
afi = db["afi"]
invoices = db["invoices"]


# =========================================
# DATE PARSER
# =========================================
def parse_date(value):

    if not value:
        return None

    formats = [

        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d"

    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                str(value),
                fmt
            )

        except:
            pass

    return None


# =========================================
# ALERTS
# =========================================
@router.get("/")
def get_alerts():

    alerts = []

    today = datetime.utcnow().date()

    # =========================================
    # BIRTHDAYS
    # =========================================
    for p in patients.find():

        birth = parse_date(
            p.get("birth_date")
        )

        if not birth:
            continue

        if (
            birth.day == today.day
            and
            birth.month == today.month
        ):

            alerts.append({

                "title":
                "Birthday",

                "patient":
                p.get("name"),

                "priority":
                "medium",

                "date":
                str(today),

                "message":
                f"🎂 Today is {p.get('name')} birthday"

            })

    # =========================================
    # VISITS
    # =========================================
    for v in visits.find():

        dt = parse_date(

            v.get("next_visit")
            or
            v.get("appointment_date")
            or
            v.get("date")

        )

        if not dt:
            continue

        diff = (
            dt.date() - today
        ).days

        if diff == 0:

            alerts.append({

                "title":
                "Today Appointment",

                "patient":
                v.get("patient_name"),

                "priority":
                "high",

                "date":
                str(dt.date()),

                "message":
                f"📅 {v.get('patient_name')} has appointment today"

            })

        elif diff == 1:

            alerts.append({

                "title":
                "Tomorrow Appointment",

                "patient":
                v.get("patient_name"),

                "priority":
                "medium",

                "date":
                str(dt.date()),

                "message":
                f"⏰ {v.get('patient_name')} has appointment tomorrow"

            })

    # =========================================
    # AFI / TREATMENT PLANS
    # =========================================
    for a in afi.find():

        dt = parse_date(
            a.get("date")
        )

        if not dt:
            continue

        diff = (
            dt.date() - today
        ).days

        if diff >= 0 and diff <= 3:

            alerts.append({

                "title":
                "Treatment Plan",

                "patient":
                a.get("patient_name"),

                "priority":
                "high",

                "date":
                str(dt.date()),

                "message":
                f"🦷 {a.get('patient_name')} treatment scheduled"

            })

    # =========================================
    # PENDING PAYMENTS
    # =========================================
    for i in invoices.find():

        balance = float(
            i.get("balance", 0)
        )

        # ONLY IF REALLY PENDING
        if balance <= 0:
            continue

        alerts.append({

            "title":
            "Pending Payment",

            "patient":
            i.get("patient_name"),

            "priority":
            "high",

            "date":
            str(today),

            "message":
            f"💰 {i.get('patient_name')} pending balance Rs {balance}"

        })

    # =========================================
    # REMOVE DUPLICATES
    # =========================================
    unique = []

    seen = set()

    for a in alerts:

        key = (
            a["title"],
            a["patient"],
            a["message"]
        )

        if key not in seen:

            seen.add(key)

            unique.append(a)

    # =========================================
    # SORT
    # =========================================
    priority_order = {

        "high": 1,
        "medium": 2,
        "low": 3
    }

    unique.sort(

        key=lambda x:
        priority_order.get(
            x["priority"],
            99
        )

    )

    return unique