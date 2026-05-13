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

invoice_collection = db["invoices"]

# ==========================================
# CREATE
# ==========================================
@router.post("/")
async def create_invoice(data: dict):

    amount = float(
        data.get("amount", 0)
    )

    discount = float(
        data.get("discount", 0)
    )

    final_amount = amount - discount

    paid = float(
        data.get("paid", 0)
    )

    data["balance"] = (
        final_amount - paid
    )

    result = invoice_collection.insert_one(data)

    data["_id"] = str(
        result.inserted_id
    )

    return data


# ==========================================
# GET
# ==========================================
@router.get("/")
async def get_invoices():

    invoices = []

    for item in invoice_collection.find():

        item["_id"] = str(item["_id"])

        invoices.append(item)

    return invoices


# ==========================================
# UPDATE
# ==========================================
@router.put("/{id}")
async def update_invoice(
    id: str,
    data: dict
):

    amount = float(
        data.get("amount", 0)
    )

    discount = float(
        data.get("discount", 0)
    )

    final_amount = amount - discount

    paid = float(
        data.get("paid", 0)
    )

    data["balance"] = (
        final_amount - paid
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


# ==========================================
# DELETE
# ==========================================
@router.delete("/{id}")
async def delete_invoice(id: str):

    invoice_collection.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }


# ==========================================
# PDF
# ==========================================
@router.get("/pdf/{patient_name}")
async def generate_pdf(
    patient_name: str
):

    invoice = invoice_collection.find_one({
        "patient_name": patient_name
    })

    if not invoice:

        return {
            "msg": "No invoice found"
        }

    filename = f"{patient_name}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    elements = []

    # ==========================================
    # TITLE
    # ==========================================
    title = Table(
        [[
            Paragraph(
                "<font color='white'><b>HDC INVOICE</b></font>",
                styles["Title"]
            )
        ]],
        colWidths=[540]
    )

    title.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,-1),
            colors.HexColor("#2563eb")
        ),

        (
            "ALIGN",
            (0,0),
            (-1,-1),
            "CENTER"
        ),

        (
            "TOPPADDING",
            (0,0),
            (-1,-1),
            18
        ),

        (
            "BOTTOMPADDING",
            (0,0),
            (-1,-1),
            18
        )

    ]))

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # PATIENT INFO
    # ==========================================
    info_data = [

        [
            "Patient",
            invoice.get(
                "patient_name",
                "-"
            )
        ],

        [
            "Date",
            invoice.get(
                "invoice_date",
                "-"
            )
        ]

    ]

    info_table = Table(
        info_data,
        colWidths=[180, 360]
    )

    info_table.setStyle(TableStyle([

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor("#d1d5db")
        ),

        (
            "BACKGROUND",
            (0,0),
            (0,-1),
            colors.HexColor("#eff6ff")
        ),

        (
            "FONTNAME",
            (0,0),
            (0,-1),
            "Helvetica-Bold"
        ),

        (
            "TOPPADDING",
            (0,0),
            (-1,-1),
            10
        ),

        (
            "BOTTOMPADDING",
            (0,0),
            (-1,-1),
            10
        )

    ]))

    elements.append(info_table)

    elements.append(
        Spacer(1, 25)
    )

    # ==========================================
    # BILLING TABLE
    # ==========================================
    table_data = [[
        "Treatment",
        "Doctor",
        "Qty",
        "Rate",
        "Category",
        "Amount"
    ]]

    rows = invoice.get(
        "rows",
        []
    )

    for row in rows:

        qty = int(
            row.get("qty", 1)
        )

        rate = float(
            row.get("rate", 0)
        )

        amount = qty * rate

        table_data.append([

            row.get(
                "treatment",
                ""
            ),

            row.get(
                "doctor",
                ""
            ),

            str(qty),

            f"Rs {rate}",

            row.get(
                "category",
                ""
            ),

            f"Rs {amount}"

        ])

    billing_table = Table(
        table_data,
        colWidths=[
            160,
            100,
            50,
            70,
            80,
            80
        ]
    )

    billing_table.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,0),
            colors.HexColor("#dbeafe")
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
            colors.HexColor("#cbd5e1")
        ),

        (
            "TOPPADDING",
            (0,0),
            (-1,-1),
            8
        ),

        (
            "BOTTOMPADDING",
            (0,0),
            (-1,-1),
            8
        ),

        (
            "ALIGN",
            (2,1),
            (-1,-1),
            "CENTER"
        )

    ]))

    elements.append(billing_table)

    elements.append(
        Spacer(1, 25)
    )

    # ==========================================
    # CATEGORY TOTALS
    # ==========================================
    category1 = 0
    category2 = 0
    category3 = 0

    for row in rows:

        qty = int(
            row.get("qty", 1)
        )

        rate = float(
            row.get("rate", 0)
        )

        total = qty * rate

        if row.get("category") == "Category 1":
            category1 += total

        elif row.get("category") == "Category 2":
            category2 += total

        elif row.get("category") == "Category 3":
            category3 += total

    summary_data = [

        [
            "Category 1",
            f"Rs {category1}"
        ],

        [
            "Category 2",
            f"Rs {category2}"
        ],

        [
            "Category 3",
            f"Rs {category3}"
        ],

        [
            "Total",
            f"Rs {invoice.get('amount', 0)}"
        ],

        [
            "Discount",
            f"Rs {invoice.get('discount', 0)}"
        ],

        [
            "Paid",
            f"Rs {invoice.get('paid', 0)}"
        ],

        [
            "Balance",
            f"Rs {invoice.get('balance', 0)}"
        ]

    ]

    summary_table = Table(
        summary_data,
        colWidths=[270, 270]
    )

    summary_table.setStyle(TableStyle([

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor("#cbd5e1")
        ),

        (
            "BACKGROUND",
            (0,0),
            (0,-1),
            colors.HexColor("#eff6ff")
        ),

        (
            "FONTNAME",
            (0,0),
            (-1,-1),
            "Helvetica-Bold"
        ),

        (
            "TOPPADDING",
            (0,0),
            (-1,-1),
            10
        ),

        (
            "BOTTOMPADDING",
            (0,0),
            (-1,-1),
            10
        ),

        (
            "ALIGN",
            (1,0),
            (1,-1),
            "CENTER"
        )

    ]))

    elements.append(summary_table)

    # ==========================================
    # BUILD
    # ==========================================
    doc.build(elements)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )