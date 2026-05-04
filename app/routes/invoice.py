from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.database import db
from bson import ObjectId
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.modules.timeline import add_to_timeline

router = APIRouter()

invoices = db["invoices"]
billing = db["billing"]
payments = db["payments"]


# =========================
# CREATE INVOICE (FIXED PATH)
# =========================
@router.post("/")   # ✅ FIXED
def create_invoice(data: dict):

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

    add_to_timeline(
        patient_id=data.get("patient_id"),
        event_type="invoice",
        ref_id=str(res.inserted_id),
        data={
            "amount": total,
            "paid": p1 + p2,
            "balance": total - (p1 + p2)
        }
    )

    return {"id": str(res.inserted_id)}


# =========================
# GET ALL
# =========================
@router.get("/")   # ✅ FIXED
def get_invoices():
    data = []
    for i in invoices.find():
        i["_id"] = str(i["_id"])
        data.append(i)
    return data


# =========================
# DELETE
# =========================
@router.delete("/{id}")   # ✅ FIXED
def delete_invoice(id: str):
    invoices.delete_one({"_id": ObjectId(id)})
    return {"msg": "Deleted"}


# =========================
# PDF (KEEP SAME)
# =========================
@router.get("/pdf/{patient_name}")   # ✅ FIXED
def generate_invoice(patient_name: str):

    try:
        bills = list(billing.find({"patient_name": patient_name}, {"_id": 0}))
        pays = list(payments.find({"patient_name": patient_name}, {"_id": 0}))

        total = sum([b.get("amount", 0) for b in bills])
        paid = sum([p.get("amount", 0) for p in pays])
        balance = total - paid

        env = Environment(loader=FileSystemLoader("app/templates"))
        template = env.get_template("invoice.html")

        html_content = template.render(
            name=patient_name,
            date=datetime.now().strftime("%Y-%m-%d"),
            bills=bills,
            payments=pays,
            total=total,
            paid=paid,
            balance=balance
        )

        pdf = HTML(string=html_content).write_pdf()

        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=invoice.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))