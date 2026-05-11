from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timedelta

router = APIRouter()

patients = db["patients"]
visits = db["visits"]

# 🔥 CHANGE THIS TO YOUR REAL AFI COLLECTION
afi = db["afi"]


# =========================================
# ALERTS
# =========================================
@router.get("/")
def get_alerts():

    alerts = []

    now = datetime.utcnow()

    today = now.date()

    # =========================================
    # BIRTHDAY ALERTS
    # =========================================
    for p in patients.find():

        birth = p.get("birth_date")

        if not birth:
            continue

        try:

            if "/" in birth:

                bday = datetime.strptime(
                    birth,
                    "%d/%m/%Y"
                )

            else:

                bday = datetime.strptime(
                    birth,
                    "%Y-%m-%d"
                )

            if (
                bday.day == today.day
                and
                bday.month == today.month
            ):

                alerts.append({

                    "type": "Birthday",

                    "priority": "medium",

                    "patient": p.get("name"),

                    "message":
                    f"🎂 Today is {p.get('name')} birthday"

                })

        except:
            pass

    # =========================================
    # UPCOMING VISITS
    # =========================================
    for v in visits.find():

        visit_date = (
            v.get("next_visit")
            or
            v.get("appointment_date")
            or
            v.get("date")
        )

        if not visit_date:
            continue

        try:

            if "/" in visit_date:

                dt = datetime.strptime(
                    visit_date,
                    "%d/%m/%Y"
                )

            else:

                dt = datetime.strptime(
                    visit_date,
                    "%Y-%m-%d"
                )

            diff = (
                dt.date() - today
            ).days

            if diff == 0:

                alerts.append({

                    "type": "Appointment",

                    "priority": "high",

                    "patient":
                    v.get("patient_name"),

                    "message":
                    f"📅 Appointment today for {v.get('patient_name')}"

                })

            elif diff == 1:

                alerts.append({

                    "type": "Appointment",

                    "priority": "medium",

                    "patient":
                    v.get("patient_name"),

                    "message":
                    f"⏰ Tomorrow appointment for {v.get('patient_name')}"

                })

        except:
            pass

    # =========================================
    # AFI / TREATMENT PLAN
    # =========================================
    for a in afi.find():

        afi_date = (
            a.get("date")
            or
            a.get("appointment_date")
            or
            a.get("next_visit")
        )

        if not afi_date:
            continue

        try:

            if "/" in afi_date:

                dt = datetime.strptime(
                    afi_date,
                    "%d/%m/%Y"
                )

            else:

                dt = datetime.strptime(
                    afi_date,
                    "%Y-%m-%d"
                )

            diff = (
                dt.date() - today
            ).days

            if diff <= 2:

                alerts.append({

                    "type": "Treatment Plan",

                    "priority": "high",

                    "patient":
                    a.get("patient_name"),

                    "message":
                    f"🦷 Planned treatment for {a.get('patient_name')}"

                })

        except:
            pass

    # =========================================
    # UNPAID INVOICES
    # =========================================
    invoices = db["invoices"]

    for i in invoices.find():

        balance = float(
            i.get("balance", 0)
        )

        if balance > 0:

            alerts.append({

                "type": "Payment",

                "priority": "high",

                "patient":
                i.get("patient_name"),

                "message":
                f"💰 Pending payment Rs {balance} for {i.get('patient_name')}"

            })

    # =========================================
    # SORT
    # =========================================
    priority_order = {

        "high": 1,
        "medium": 2,
        "low": 3
    }

    alerts.sort(
        key=lambda x:
        priority_order.get(
            x["priority"],
            99
        )
    )

    return alerts