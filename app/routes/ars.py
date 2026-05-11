from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

router = APIRouter()

patients = db["patients"]
visits = db["visits"]
invoices = db["invoices"]
lab_cases = db["lab_cases"]
afi = db["afi"]

# ==========================================
# GET ALERTS
# ==========================================
@router.get("/")
def get_alerts():

    alerts = []

    today = datetime.utcnow().date()

    # ==========================================
    # VISIT APPOINTMENTS
    # ==========================================
    for v in visits.find():

        next_visit = v.get("next_visit")

        if next_visit:

            try:

                visit_date = datetime.strptime(
                    next_visit,
                    "%Y-%m-%d"
                ).date()

                diff = (
                    visit_date - today
                ).days

                if diff == 1:

                    alerts.append({

                        "type":
                        "appointment",

                        "priority":
                        "medium",

                        "title":
                        "Tomorrow Appointment",

                        "message":
                        f"{v.get('patient_name')} has appointment tomorrow.",

                        "date":
                        next_visit
                    })

                elif diff == 0:

                    alerts.append({

                        "type":
                        "appointment",

                        "priority":
                        "high",

                        "title":
                        "Today's Appointment",

                        "message":
                        f"{v.get('patient_name')} appointment is today.",

                        "date":
                        next_visit
                    })

                elif diff < 0:

                    alerts.append({

                        "type":
                        "appointment",

                        "priority":
                        "critical",

                        "title":
                        "Missed Appointment",

                        "message":
                        f"{v.get('patient_name')} missed appointment.",

                        "date":
                        next_visit
                    })

            except:
                pass

    # ==========================================
    # AFI FUTURE TREATMENTS
    # ==========================================
    for a in afi.find():

        visit_date = a.get("date")

        status = (
            a.get("status", "")
            .lower()
        )

        if visit_date and status != "completed":

            try:

                d = datetime.strptime(
                    visit_date,
                    "%Y-%m-%d"
                ).date()

                diff = (
                    d - today
                ).days

                if diff == 0:

                    alerts.append({

                        "type":
                        "afi",

                        "priority":
                        "high",

                        "title":
                        "Today's Treatment Plan",

                        "message":
                        f"{a.get('patient_name')} has planned treatment today.",

                        "date":
                        visit_date
                    })

                elif diff > 0 and diff <= 3:

                    alerts.append({

                        "type":
                        "afi",

                        "priority":
                        "medium",

                        "title":
                        "Upcoming Treatment",

                        "message":
                        f"{a.get('patient_name')} treatment scheduled soon.",

                        "date":
                        visit_date
                    })

                elif diff < 0:

                    alerts.append({

                        "type":
                        "afi",

                        "priority":
                        "critical",

                        "title":
                        "Missed Treatment Plan",

                        "message":
                        f"{a.get('patient_name')} missed planned treatment.",

                        "date":
                        visit_date
                    })

            except:
                pass

    # ==========================================
    # BIRTHDAY ALERTS
    # ==========================================
    for p in patients.find():

        birth = p.get("birth_date")

        if birth:

            try:

                b = datetime.strptime(
                    birth,
                    "%Y-%m-%d"
                )

                if (
                    b.day == today.day
                    and
                    b.month == today.month
                ):

                    alerts.append({

                        "type":
                        "birthday",

                        "priority":
                        "low",

                        "title":
                        "Patient Birthday",

                        "message":
                        f"Today is {p.get('name')} birthday 🎂",

                        "date":
                        str(today)
                    })

            except:
                pass

    # ==========================================
    # PENDING PAYMENTS
    # ==========================================
    for i in invoices.find():

        balance = float(
            i.get("balance", 0)
        )

        if balance > 0:

            alerts.append({

                "type":
                "payment",

                "priority":
                "high",

                "title":
                "Pending Payment",

                "message":
                f"{i.get('patient_name')} has pending balance Rs {balance}",

                "date":
                str(today)
            })

    # ==========================================
    # LAB DEADLINES
    # ==========================================
    for c in lab_cases.find():

        deadline = c.get("delivery_date")

        status = (
            c.get("status", "")
            .lower()
        )

        if deadline and status != "completed":

            try:

                d = datetime.strptime(
                    deadline,
                    "%Y-%m-%d"
                ).date()

                diff = (
                    d - today
                ).days

                if diff < 0:

                    alerts.append({

                        "type":
                        "lab",

                        "priority":
                        "critical",

                        "title":
                        "Lab Case Overdue",

                        "message":
                        f"{c.get('patient_name')} lab case is overdue.",

                        "date":
                        deadline
                    })

                elif diff <= 2:

                    alerts.append({

                        "type":
                        "lab",

                        "priority":
                        "medium",

                        "title":
                        "Lab Delivery Soon",

                        "message":
                        f"{c.get('patient_name')} lab delivery approaching.",

                        "date":
                        deadline
                    })

            except:
                pass

    # ==========================================
    # SORT
    # ==========================================
    priority_order = {

        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }

    alerts.sort(

        key=lambda x:

        priority_order.get(
            x["priority"],
            5
        )
    )

    return alerts