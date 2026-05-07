from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.database import db
from bson import ObjectId
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

router = APIRouter()

invoices = db["invoices"]
patients = db["patients"]


# =========================
# CREATE
# =========================
@router.post("/")
def create_invoice(data: dict):

    patient_name = data.get("patient_name")
    rows = data.get("rows", [])
    payments = data.get("payments", [])
    discount = float(data.get("discount", 0))

    if not patient_name:
        raise HTTPException(status_code=400, detail="Patient required")

    total = sum(float(r.get("rate", 0)) for r in rows)
    paid = sum(float(p.get("amount", 0)) for p in payments)

    final = total - discount

    # if discount exists → balance = 0
    balance = 0 if discount > 0 else (final - paid)

    invoice = {
        "patient_name": patient_name,
        "rows": rows,
        "payments": payments,

        "amount": total,
        "discount": discount,
        "final": final,

        "paid": paid,
        "balance": balance,

        "created_at": datetime.utcnow()
    }

    res = invoices.insert_one(invoice)

    return {
        "id": str(res.inserted_id)
    }


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update_invoice(id: str, data: dict):

    try:

        rows = data.get("rows", [])
        payments = data.get("payments", [])
        discount = float(data.get("discount", 0))

        total = sum(float(r.get("rate", 0)) for r in rows)
        paid = sum(float(p.get("amount", 0)) for p in payments)

        final = total - discount

        balance = 0 if discount > 0 else (final - paid)

        data.update({
            "amount": total,
            "final": final,
            "paid": paid,
            "balance": balance
        })

        invoices.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

        return {
            "msg": "Updated ✅"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================
# GET
# =========================
@router.get("/")
def get_invoices():

    data = []

    for i in invoices.find():

        i["_id"] = str(i["_id"])

        data.append(i)

    return data


# =========================
# DELETE
# =========================
@router.delete("/{id}")
def delete_invoice(id: str):

    invoices.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }


# =========================
# PDF
# =========================
@router.get("/pdf/{patient_name}")
def generate_invoice(patient_name: str):

    inv = list(
        invoices.find(
            {"patient_name": patient_name},
            {"_id": 0}
        )
    )

    if not inv:
        return {"msg": "No invoice"}

    bills = []
    payments = []

    total = 0
    discount = 0
    paid = 0

    # =========================
    # BUILD DATA
    # =========================
    for i in inv:

        # ROWS
        for r in i.get("rows", []):

            bills.append({
                "procedure": r.get("treatment"),
                "qty": r.get("qty", ""),
                "rate": r.get("rate"),
                "amount": r.get("rate")
            })

        # PAYMENTS
        payments.extend(
            i.get("payments", [])
        )

        total += float(
            i.get("amount", 0)
        )

        discount += float(
            i.get("discount", 0)
        )

        paid += float(
            i.get("paid", 0)
        )

    final = total - discount

    balance = (
        0 if discount > 0
        else (final - paid)
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
    # PATIENT COLOR INFO
    # =========================
    patient = patients.find_one({
        "name": patient_name
    }) or {}

    # =========================
    # RENDER HTML
    # =========================
    html_content = template.render(

        patient=patient,

        name=patient_name,

        date=datetime.now().strftime(
            "%Y-%m-%d"
        ),

        bills=bills,

        payments=payments,

        total=total,

        discount=discount,

        paid=paid,

        balance=balance
    )

    # =========================
    # GENERATE PDF
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