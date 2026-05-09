from fastapi import APIRouter
from fastapi.responses import Response
from app.core.database import db
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

router = APIRouter()

patients = db["patients"]

# =========================
# PDF FROM FIS
# =========================
@router.get("/pdf/{patient_name}")
def generate_invoice(patient_name: str):

    billing = db["billing"]

    inv = list(
        billing.find(
            {"patient_name": patient_name}
        )
    )

    if not inv:
        return {"msg": "No invoice"}

    bills = []

    total = 0

    for i in inv:

        bills.append({
            "procedure": i.get("procedure"),
            "qty": 1,
            "rate": i.get("amount", 0),
            "amount": i.get("amount", 0)
        })

        total += float(
            i.get("amount", 0)
        )

    env = Environment(
        loader=FileSystemLoader(
            "app/templates"
        )
    )

    template = env.get_template(
        "invoice.html"
    )

    patient = patients.find_one({
        "name": patient_name
    }) or {}

    html_content = template.render(

        patient=patient,

        name=patient_name,

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