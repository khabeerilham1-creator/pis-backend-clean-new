from fastapi import APIRouter
from fastapi.responses import Response
from app.core.database import db
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from urllib.parse import unquote

router = APIRouter()

billing = db["billing"]
patients = db["patients"]


# =========================
# GET ALL INVOICES FROM FIS
# =========================
@router.get("/")
def get_invoices():

    data = []

    for i in billing.find():

        i["_id"] = str(i["_id"])

        data.append(i)

    return data


# =========================
# PDF GENERATOR
# =========================
@router.get("/pdf/{patient_name}")
def generate_invoice(patient_name: str):

    decoded_name = unquote(patient_name).strip()

    # 🔥 DEBUG
    print("SEARCHING:", decoded_name)

    # 🔥 LOAD BILLING
    invoices = list(
        billing.find()
    )

    matched = []

    for i in invoices:

        db_name = str(
            i.get("patient_name", "")
        ).strip()

        print("DB:", db_name)

        if db_name.lower() == decoded_name.lower():

            matched.append(i)

    if not matched:

        return {
            "msg": "No invoice",
            "searched": decoded_name
        }

    bills = []

    total = 0

    # =========================
    # BUILD BILL DATA
    # =========================
    for i in matched:

        bills.append({

            "procedure":
                i.get("procedure", ""),

            "qty": 1,

            "rate":
                i.get("amount", 0),

            "amount":
                i.get("amount", 0)
        })

        total += float(
            i.get("amount", 0)
        )

    # =========================
    # TEMPLATE
    # =========================
    env = Environment(
        loader=FileSystemLoader(
            "app/templates"
        )
    )

    template = env.get_template(
        "invoice.html"
    )

    # =========================
    # PATIENT
    # =========================
    patient = patients.find_one({
        "name": {
            "$regex":
                f"^{decoded_name}$",
            "$options": "i"
        }
    }) or {}

    # =========================
    # RENDER
    # =========================
    html_content = template.render(

        patient=patient,

        name=decoded_name,

        date=datetime.now().strftime(
            "%Y-%m-%d"
        ),

        bills=bills,

        payments=[],

        total=total,

        discount=0,

        paid=0,

        balance=total
    )

    # =========================
    # PDF
    # =========================
    pdf = HTML(
        string=html_content
    ).write_pdf()

    return Response(

        content=pdf,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
            "inline; filename=invoice.pdf"
        }
    )