from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.core.database import db
from bson import ObjectId
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

router = APIRouter()

invoices = db["invoices"]
payments = db["payments"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


# =========================
# CREATE INVOICE
# =========================
@router.post("/invoice")
async def create_invoice(data: dict):

    qty = float(data.get("qty", 0))
    rate = float(data.get("rate", 0))

    total = qty * rate
    paid = float(data.get("payment1", 0)) + float(data.get("payment2", 0))

    invoice = {
        "patient_name": data.get("patient_name"),
        "procedure": data.get("procedure"),
        "qty": qty,
        "rate": rate,
        "amount": total,
        "paid": paid,
        "balance": total - paid,
        "created_at": datetime.now()
    }

    invoices.insert_one(invoice)

    return {"msg": "Invoice created"}


# =========================
# GET ALL INVOICES
# =========================
@router.get("/invoices")
def get_invoices():
    data = []
    for i in invoices.find():
        i["_id"] = str(i["_id"])
        data.append(i)
    return data


# =========================
# GENERATE PDF
# =========================
@router.get("/invoice-pdf/{name}")
def generate_invoice_pdf(name: str):

    bills = list(invoices.find({"patient_name": name}))
    pays = list(payments.find({"patient_name": name}))

    total = sum([b.get("amount", 0) for b in bills])
    paid = sum([b.get("paid", 0) for b in bills])
    balance = total - paid

    template = env.get_template("invoice.html")

    html = template.render(
        date=datetime.now().strftime("%d-%b-%Y"),
        name=name,
        bills=bills,
        payments=pays,
        total=total,
        paid=paid,
        balance=balance
    )

    file_path = os.path.join(UPLOAD_DIR, f"invoice_{name}.pdf")

    HTML(string=html, base_url=BASE_DIR).write_pdf(file_path)

    return FileResponse(file_path, media_type="application/pdf")