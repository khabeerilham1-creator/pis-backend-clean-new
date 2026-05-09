from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.core.database import db
from bson import ObjectId

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

router = APIRouter()

# 🔥 FIXED COLLECTION
invoice_collection = db["invoices"]

# =========================
# CREATE
# =========================
@router.post("/")
async def create_invoice(data: dict):

    total_paid = sum([
        float(p.get("amount", 0))
        for p in data.get("payments", [])
    ])

    amount = float(
        data.get("amount", 0)
    )

    data["paid"] = total_paid

    data["balance"] = (
        amount - total_paid
    )

    result = invoice_collection.insert_one(data)

    data["_id"] = str(
        result.inserted_id
    )

    return data


# =========================
# GET ALL
# =========================
@router.get("/")
async def get_invoices():

    data = []

    for item in invoice_collection.find():

        item["_id"] = str(item["_id"])

        data.append(item)

    return data


# =========================
# UPDATE
# =========================
@router.put("/{id}")
async def update_invoice(
    id: str,
    data: dict
):

    total_paid = sum([
        float(p.get("amount", 0))
        for p in data.get("payments", [])
    ])

    amount = float(
        data.get("amount", 0)
    )

    data["paid"] = total_paid

    data["balance"] = (
        amount - total_paid
    )

    invoice_collection.update_one(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": data
        }
    )

    return {
        "msg": "Updated"
    }


# =========================
# DELETE
# =========================
@router.delete("/{id}")
async def delete_invoice(id: str):

    invoice_collection.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }


# =========================
# PDF
# =========================
@router.get("/pdf/{patient_name}")
async def generate_pdf(
    patient_name: str
):

    invoice = invoice_collection.find_one({
        "patient_name": patient_name
    })

    if not invoice:

        return {
            "msg": "No invoice"
        }

    filename = (
        f"{patient_name}.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    elements = []

    # =========================
    # TITLE
    # =========================
    title = Paragraph(
        f"<b>Invoice - {patient_name}</b>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    # =========================
    # PATIENT
    # =========================
    patient = Paragraph(
        f"<b>Patient:</b> {patient_name}",
        styles["Heading2"]
    )

    elements.append(patient)

    elements.append(
        Spacer(1, 20)
    )

    # =========================
    # TABLE
    # =========================
    data = [
        [
            "Procedure",
            "Doctor",
            "Qty",
            "Rate",
            "Amount"
        ]
    ]

    rows = invoice.get("rows", [])

    # OLD DATA SUPPORT
    if not rows:

        procedures = (
            invoice.get(
                "procedure",
                ""
            ).split(",")
        )

        doctors = (
            invoice.get(
                "doctor",
                ""
            ).split(",")
        )

        for i, proc in enumerate(
            procedures
        ):

            amount_per = int(
                invoice.get(
                    "amount",
                    0
                ) / len(procedures)
            )

            data.append([

                proc.strip(),

                doctors[i].strip()
                if i < len(doctors)
                else "",

                "1",

                str(amount_per),

                str(amount_per)

            ])

    else:

        for row in rows:

            qty = int(
                row.get("qty", 1)
            )

            rate = float(
                row.get("rate", 0)
            )

            data.append([

                row.get(
                    "treatment",
                    ""
                ),

                row.get(
                    "doctor",
                    ""
                ),

                str(qty),

                str(rate),

                str(qty * rate)

            ])

    table = Table(
        data,
        colWidths=[
            180,
            120,
            50,
            70,
            80
        ]
    )

    table.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,0),
            colors.lightgrey
        ),

        (
            "TEXTCOLOR",
            (0,0),
            (-1,0),
            colors.black
        ),

        (
            "FONTNAME",
            (0,0),
            (-1,0),
            "Helvetica-Bold"
        ),

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.black
        ),

        (
            "BOTTOMPADDING",
            (0,0),
            (-1,0),
            10
        ),

        (
            "ALIGN",
            (2,1),
            (-1,-1),
            "CENTER"
        )

    ]))

    elements.append(table)

    elements.append(
        Spacer(1, 30)
    )

    # =========================
    # SUMMARY
    # =========================
    summary = Table([

        [
            "Total",
            invoice.get(
                "amount",
                0
            )
        ],

        [
            "Discount",
            invoice.get(
                "discount",
                0
            )
        ],

        [
            "Paid",
            invoice.get(
                "paid",
                0
            )
        ],

        [
            "Balance",
            invoice.get(
                "balance",
                0
            )
        ]

    ],
    colWidths=[
        200,
        150
    ])

    summary.setStyle(TableStyle([

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.black
        ),

        (
            "FONTNAME",
            (0,0),
            (-1,-1),
            "Helvetica-Bold"
        ),

        (
            "BACKGROUND",
            (0,0),
            (-1,-1),
            colors.whitesmoke
        )

    ]))

    elements.append(summary)

    doc.build(elements)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )