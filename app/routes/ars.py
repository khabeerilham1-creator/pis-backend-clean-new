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
    # VISITS ALERTS
    # =========================
    for v in visits.find():

        print("VISIT DATA:", v)

        visit_date = (

            v.get("date")

            or v.get("visit_date")

            or v.get("appointment_date")

        )

        if not visit_date:
            continue

        try:

            visit_day = datetime.strptime(
                str(visit_date),
                "%Y-%m-%d"
            ).date()

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

        except Exception as e:

            print("VISIT ALERT ERROR:", e)

    # =========================
    # AFI ALERTS
    # =========================
    for a in afi.find():

        print("AFI DATA:", a)

        afi_date = (

            a.get("date")

            or a.get("appointment_date")

            or a.get("visit_date")

        )

        if not afi_date:
            continue

        try:

            afi_day = datetime.strptime(
                str(afi_date),
                "%Y-%m-%d"
            ).date()

            patient_name = (

                a.get("patient_name")

                or a.get("patient")

                or a.get("name")

                or a.get("patientName")

                or a.get("full_name")

                or a.get("patient_id")

                or "Unknown Patient"
            )

            treatment = (

                a.get("treatment")

                or a.get("procedure")

                or a.get("plan")

                or "Treatment"

            )

            # TODAY
            if afi_day == today:

                alerts.append({

                    "title":
                    "Today Appointment",

                    "message":
                    f"📅 {patient_name} has appointment today",

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
                    "Upcoming Appointment",

                    "message":
                    f"🗓️ {patient_name} appointment on {afi_day}",

                    "priority":
                    "low",

                    "date":
                    str(afi_day)
                })

        except Exception as e:

            print("AFI ALERT ERROR:", e)

    # =========================
    # PAYMENT ALERTS
    # =========================
    for i in invoices.find():

        amount = float(
            i.get("amount", 0)
        )

        paid = float(
            i.get("paid", 0)
        )

        balance = amount - paid

        if balance > 0:

            patient_name = (
                i.get("patient_name")
                or "Unknown Patient"
            )

            alerts.append({

                "title":
                "Pending Payment",

                "message":
                f"💰 Pending payment Rs {balance} for {patient_name}",

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
        key=lambda x: x["message"]
    )

    return alerts