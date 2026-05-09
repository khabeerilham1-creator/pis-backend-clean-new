from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.database import db
from bson import ObjectId
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from urllib.parse import unquote

router = APIRouter()

# =========================
# COLLECTIONS
# =========================
invoices = db["invoices"]
billing = db["billing"]
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
        raise HTTPException(
            status_code=400,
            detail="Patient required"
        )

    total = sum(
        float(r.get("rate", 0))
        for r in rows
    )

    paid = sum(
        float(p.get("amount", 0))
        for p in payments
    )

    final = total - discount

    balance = (
        0 if discount > 0
        else (final - paid)
    )

    invoice = {

        "patient_name":
            patient_name,

        "rows":
            rows,

        "payments":
            payments,

        "amount":
            total,

        "discount":
            discount,

        "final":
            final,

        "paid":
            paid,

        "balance":
            balance,

        "created_at":
            datetime.utcnow()
    }

    res = invoices.insert_one(
        invoice
    )

    return {
        "id":
            str(res.inserted_id)
    }


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update_invoice(id: str, data: dict):

    try:

        rows = data.get("rows", [])
        payments = data.get("payments", [])
        discount = float(
            data.get("discount", 0)
        )

        total = sum(
            float(r.get("rate", 0))
            for r in rows
        )

        paid = sum(
            float(p.get("amount", 0))
            for p in payments
        )

        final = total - discount

        balance = (
            0 if discount > 0
            else (final - paid)
        )

        data.update({

            "amount":
                total,

            "final":
                final,

            "paid":
                paid,

            "balance":
                balance
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

    # 🔥 NORMAL INVOICES
    for i in invoices.find():

        i["_id"] = str(i["_id"])

        data.append(i)

    # 🔥 FIS RECORDS
    for b in billing.find():

        data.append({

            "_id":
                str(b["_id"]),

            "patient_name":
                b.get("patient_name"),

            "amount":
                b.get("amount", 0),

            "paid":
                0,

            "balance":
                b.get("amount", 0),

            "procedure":
                b.get("procedure", ""),

            "from_fis":
                True
        })

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

    decoded_name = unquote(
        patient_name
    )

    # =========================
    # NORMAL INVOICE
    # =========================
    inv = list(

        invoices.find(

            {
                "patient_name": {
                    "$regex":
                        f"^{decoded_name}$",

                    "$options":
                        "i"
                }
            },

            {"_id": 0}
        )
    )

    # =========================
    # IF NOT FOUND LOAD FIS
    # =========================
    if not inv:

        fis_data = list(

            billing.find(

                {
                    "patient_name": {
                        "$regex":
                            f"^{decoded_name}$",

                        "$options":
                            "i"
                    }
                }
            )
        )

        if not fis_data:

            return {
                "msg": "No invoice"
            }

        inv = []

        for f in fis_data:

            inv.append({

                "rows": [{

                    "treatment":
                        f.get("procedure"),

                    "qty":
                        1,

                    "rate":
                        f.get("amount", 0)
                }],

                "payments": [],

                "amount":
                    f.get("amount", 0),

                "discount":
                    0,

                "paid":
                    0
            })

    bills = []
    payments = []

    total = 0
    discount = 0
    paid = 0

    # =========================
    # BUILD DATA
    # =========================
    for i in inv:

        for r in i.get("rows", []):

            bills.append({

                "procedure":
                    r.get("treatment"),

                "qty":
                    r.get("qty", ""),

                "rate":
                    r.get("rate"),

                "amount":
                    r.get("rate")
            })

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
    # PATIENT
    # =========================
    patient = patients.find_one({

        "name": {

            "$regex":
                f"^{decoded_name}$",

            "$options":
                "i"
        }

    }) or {}

    # =========================
    # RENDER HTML
    # =========================
    html_content = template.render(

        patient=patient,

        name=decoded_name,

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