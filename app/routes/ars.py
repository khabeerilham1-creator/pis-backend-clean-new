from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timedelta

router = APIRouter()

patients = db["patients"]
visits = db["visits"]
afi = db["afi"]
invoices = db["invoices"]

# =========================
# GET ALERTS
# =========================
@router.get("/")
def get_alerts():

    alerts = []

    today = datetime.utcnow().date()

    next_7_days = today + timedelta(days=7)

    # =========================
    # BIRTHDAY ALERTS
    # =========================
    for p in patients.find():

        birth_date = p.get("birth_date")

        if not birth_date:
            continue

        try:

            dob = datetime.strptime(
                birth_date,
                "%Y-%m-%d"
            ).date()

            current_year_bday = dob.replace(
                year=today.year
            )

            patient_name = (
                p.get("name")
                or "Unknown Patient"
            )

            # TODAY
            if current_year_bday == today:

                alerts.append({

                    "title":
                    "Birthday Today",

                    "message":
                    f"🎂 {patient_name} birthday is today",

                    "priority":
                    "medium",

                    "date":
                    str(current_year_bday)
                })

            # UPCOMING
            elif (
                today <
                current_year_bday <=
                next_7_days
            ):

                alerts.append({

                    "title":
                    "Upcoming Birthday",

                    "message":
                    f"🎂 {patient_name} birthday on {current_year_bday}",

                    "priority":
                    "low",

                    "date":
                    str(current_year_bday)
                })

        except:
            pass

    # =========================
    # VISIT ALERTS
    # =========================
    for v in visits.find():

        visit_date = (
            v.get("date")
            or v.get("visit_date")
            or v.get("appointment_date")
        )

        if not visit_date:
            continue

        try:

            visit_day = datetime.strptime(
                visit_date,
                "%Y-%m-%d"
            ).date()

            # 🔥 AUTO DETECT PATIENT FIELD
            patient_name = (

                v.get("patient_name")

                or v.get("patient")

                or v.get("name")

                or v.get("patientName")

                or v.get("full_name")

                or "Unknown Patient"
            )

            # TODAY
            if visit_day == today:

                alerts.append({

                    "title":
                    "Visit Today",

                    "message":
                    f"📅 {patient_name} has visit today",

                    "priority":
                    "high",

                    "date":
                    str(visit_day)
                })

            # UPCOMING
            elif (
                today <
                visit_day <=
                next_7_days
            ):

                alerts.append({

                    "title":
                    "Upcoming Visit",

                    "message":
                    f"🗓️ {patient_name} upcoming visit on {visit_day}",

                    "priority":
                    "low",

                    "date":
                    str(visit_day)
                })

        except:
            pass

    # =========================
    # AFI / TREATMENT ALERTS
    # =========================
    for a in afi.find():

        afi_date = (
            a.get("date")
            or a.get("appointment_date")
        )

        if not afi_date:
            continue

        try:

            afi_day = datetime.strptime(
                afi_date,
                "%Y-%m-%d"
            ).date()

            patient_name = (

                a.get("patient_name")

                or a.get("patient")

                or a.get("name")

                or "Unknown Patient"
            )

            treatment = (
                a.get("treatment")
                or a.get("procedure")
                or "Treatment"
            )

            # TODAY
            if afi_day == today:

                alerts.append({

                    "title":
                    "Treatment Today",

                    "message":
                    f"🦷 {patient_name} treatment today ({treatment})",

                    "priority":
                    "high",

                    "date":
                    str(afi_day)
                })

            # UPCOMING
            elif (
                today <
                afi_day <=
                next_7_days
            ):

                alerts.append({

                    "title":
                    "Upcoming Treatment",

                    "message":
                    f"🦷 {patient_name} treatment on {afi_day}",

                    "priority":
                    "medium",

                    "date":
                    str(afi_day)
                })

        except:
            pass

    # =========================
    # PAYMENT ALERTS
    # =========================
    for i in invoices.find():

        balance = float(
            i.get("balance", 0)
        )

        paid = float(
            i.get("paid", 0)
        )

        amount = float(
            i.get("amount", 0)
        )

        # 🔥 FIX FALSE BALANCES
        real_balance = amount - paid

        if real_balance > 0:

            patient_name = (
                i.get("patient_name")
                or "Unknown Patient"
            )

            alerts.append({

                "title":
                "Pending Payment",

                "message":
                f"💰 Pending payment Rs {real_balance} for {patient_name}",

                "priority":
                "high",

                "date":
                str(today)
            })

    # =========================
    # SORT A-Z
    # =========================
    alerts = sorted(
        alerts,
        key=lambda x: x["message"]
    )

    return alerts