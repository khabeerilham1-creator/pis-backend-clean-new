from fastapi import APIRouter
from app.core.database import db
from datetime import datetime

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
invoices = db["invoices"]

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


# =========================
# MAIN DASHBOARD
# =========================
@router.get("/")
def dashboard(month: int = None, year: int = None):

    now = datetime.utcnow()

    selected_month = month or now.month
    selected_year = year or now.year

    today = now.date()

    total_patients = patients.count_documents({})
    total_checkups = checkups.count_documents({})

    monthly_revenue = 0
    today_revenue = 0

    doctor_share = 0
    lab_total = 0
    owner_profit = 0

    # =========================
    # LOOP INVOICES
    # =========================
    for i in invoices.find():

        created = i.get("created_at")

        if not created:
            continue

        # =========================
        # FINAL BILL ONLY
        # =========================
        amount = float(

            i.get(
                "final",

                i.get("amount", 0)
            )
        )

        # =========================
        # MONTH FILTER
        # =========================
        if (
            created.month == selected_month
            and
            created.year == selected_year
        ):

            monthly_revenue += amount

            # SPLITS
            lab = float(
                i.get("lab_charge", 0)
            )

            doc = amount * 0.25

            owner = (
                amount
                - doc
                - lab
            )

            doctor_share += doc
            lab_total += lab
            owner_profit += owner

        # TODAY REVENUE
        if created.date() == today:

            today_revenue += amount

    # =========================
    # AVAILABLE MONTHS
    # =========================
    available_months = []

    months = invoices.aggregate([

        {
            "$group": {

                "_id": {

                    "year": {
                        "$year": "$created_at"
                    },

                    "month": {
                        "$month": "$created_at"
                    }
                }
            }
        },

        {
            "$sort": {

                "_id.year": -1,
                "_id.month": -1
            }
        }
    ])

    for m in months:

        month_no = m["_id"]["month"]

        available_months.append({

            "year":
            m["_id"]["year"],

            "month":
            month_no,

            "month_name":
            MONTHS[month_no - 1]
        })

    return {

        "patients":
        total_patients,

        "checkups":
        total_checkups,

        # 🔥 MONTHLY REVENUE
        "revenue":
        monthly_revenue,

        "today_revenue":
        today_revenue,

        "today_patients":
        0,

        "selected_month":
        selected_month,

        "selected_year":
        selected_year,

        "available_months":
        available_months,

        "split": {

            "doctor":
            doctor_share,

            "lab":
            lab_total,

            "owner":
            owner_profit
        }
    }


# =========================
# DAILY ENDPOINT
# =========================
@router.get("/daily")
def daily():

    today = datetime.utcnow().date()

    today_revenue = 0

    for i in invoices.find():

        created = i.get("created_at")

        if not created:
            continue

        amount = float(
            i.get(
                "final",
                i.get("amount", 0)
            )
        )

        if created.date() == today:

            today_revenue += amount

    return {

        "today_revenue":
        today_revenue
    }