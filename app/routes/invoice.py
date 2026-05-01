from fastapi import APIRouter
from fastapi.responses import Response
from app.core.database import db
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
from bson import ObjectId

router = APIRouter()

# Collections
billing = db["billing"]
payments = db["payments"]
invoices = db["invoices"]


# =========================
# CREATE INVOICE (MANUAL SAVE)
# =========================
@router.post("/invoice")
async def create_invoice(data: dict):

    qty = float(data.get("qty", 0))
    rate = float(data.get("rate", 0))

    total = qty * rate

    p1 = float(data.get("payment1", 0))
    p2 = float(data.get("payment2", 0))

    invoice = {
        "patient_name": data.get("patient_name"),
        "procedure": data.get("procedure"),
        "qty": qty,
        "rate": rate,
        "amount": total,
        "paid": p1 + p2,
        "balance": total - (p1 + p2),
        "created_at": datetime.utcnow()
    }

    res = invoices.insert_one(invoice)
    return {"id": str(res.inserted_id)}


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
# UPDATE INVOICE
# =========================
@router.put("/invoice/{id}")
async def update_invoice(id: str, data: dict):
    invoices.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"msg": "Updated"}


# =========================
# DELETE INVOICE
# =========================
@router.delete("/invoice/{id}")
def delete_invoice(id: str):
    invoices.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}


# =========================
# 🔥 GENERATE PDF
# =========================
@router.get("/invoice-pdf/{patient_name}")
def generate_invoice(patient_name: str):

    bills = list(billing.find({"patient_name": patient_name}))
    payments_data = list(payments.find({"patient_name": patient_name}))

    total = sum([b.get("amount", 0) for b in bills])
    paid = sum([p.get("amount", 0) for p in payments_data])
    balance = total - paid

    # LOAD TEMPLATE
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("invoice.html")

    html_content = template.render(
        name=patient_name,
        bills=bills,
        payments=payments_data,
        total=total,
        paid=paid,
        balance=balance,
        date=datetime.now().strftime("%d-%m-%Y")
    )

    pdf = HTML(string=html_content).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=invoice_{patient_name}.pdf"
        }
    )