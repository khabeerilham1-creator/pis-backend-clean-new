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
    # VISITS ALERTS
    # =========================================
    for v in visits.find():

        patient_name = (

            v.get("patient_name")

            or v.get("name")

            or v.get("patient")

            or "Unknown Patient"
        )

        visit_date = (

            v.get("next_visit")

            or v.get("appointment_date")

            or v.get("date")
        )

        dt = parse_date(
            visit_date
        )

        if not dt:
            continue

        diff = (
            dt.date() - today
        ).days

        # TODAY
        if diff == 0:

            alerts.append({

                "title":
                "Visit Today",

                "patient":
                patient_name,

                "priority":
                "high",

                "date":
                str(dt.date()),

                "message":
                f"📅 {patient_name} has visit today"

            })

        # TOMORROW
        elif diff == 1:

            alerts.append({

                "title":
                "Visit Tomorrow",

                "patient":
                patient_name,

                "priority":
                "medium",

                "date":
                str(dt.date()),

                "message":
                f"⏰ {patient_name} has visit tomorrow"

            })

        # NEXT 7 DAYS
        elif diff > 1 and diff <= 7:

            alerts.append({

                "title":
                "Upcoming Visit",

                "patient":
                patient_name,

                "priority":
                "low",

                "date":
                str(dt.date()),

                "message":
                f"🗓️ {patient_name} upcoming visit on {dt.date()}"

            })

    # =========================================
    # AFI ALERTS
    # =========================================
    for a in afi.find():

        patient_name = (

            a.get("patient_name")

            or a.get("name")

            or a.get("patient")

            or "Unknown Patient"
        )

        afi_date = (

            a.get("date")

            or a.get("appointment_date")

            or a.get("next_visit")
        )

        dt = parse_date(
            afi_date
        )

        if not dt:
            continue

        diff = (
            dt.date() - today
        ).days

        # TODAY
        if diff == 0:

            alerts.append({

                "title":
                "Treatment Today",

                "patient":
                patient_name,

                "priority":
                "high",

                "date":
                str(dt.date()),

                "message":
                f"🦷 {patient_name} treatment today"

            })

        # TOMORROW
        elif diff == 1:

            alerts.append({

                "title":
                "Treatment Tomorrow",

                "patient":
                patient_name,

                "priority":
                "medium",

                "date":
                str(dt.date()),

                "message":
                f"⏰ {patient_name} treatment tomorrow"

            })

        # NEXT 7 DAYS
        elif diff > 1 and diff <= 7:

            alerts.append({

                "title":
                "Upcoming Treatment",

                "patient":
                patient_name,

                "priority":
                "low",

                "date":
                str(dt.date()),

                "message":
                f"🗓️ {patient_name} treatment on {dt.date()}"

            })

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
    # REMOVE DUPLICATES
    # =========================================
    final_alerts = []

    seen = set()

    for a in alerts:

        key = (
            a["title"],
            a["patient"],
            a["date"]
        )

        if key not in seen:

            seen.add(key)

            final_alerts.append(a)

    # =========================================
    # SORT
    # =========================================
    priority_order = {

        "high": 1,
        "medium": 2,
        "low": 3
    }

    final_alerts.sort(

        key=lambda x:
        priority_order.get(
            x["priority"],
            99
        )

    )

    return final_alerts