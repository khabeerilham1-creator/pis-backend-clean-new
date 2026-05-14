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
from reportlab.lib.pagesizes import A4

import os

router = APIRouter()

invoice_collection = db["invoices"]

# ==========================================
# CREATE INVOICE
# ==========================================
@router.post("/")
async def create_invoice(data: dict):

    amount = float(
        data.get("amount", 0)
    )

    discount = float(
        data.get("discount", 0)
    )

    paid = float(
        data.get("paid", 0)
    )

    final_amount = amount - discount

    balance = final_amount - paid

    data["balance"] = balance

    result = invoice_collection.insert_one(data)

    data["_id"] = str(
        result.inserted_id
    )

    return data


# ==========================================
# GET ALL
# ==========================================
@router.get("/")
async def get_invoices():

    invoices = []

    for item in invoice_collection.find():

        item["_id"] = str(item["_id"])

        invoices.append(item)

    return invoices


# ==========================================
# PDF
# ==========================================
@router.get("/pdf/{invoice_id}")
async def generate_pdf(
    invoice_id: str
):

    # ==========================================
    # FIX INVALID OBJECT ID
    # ==========================================
    try:

        obj_id = ObjectId(
            invoice_id
        )

    except:

        return {
            "msg": "Invalid invoice id"
        }

    invoice = invoice_collection.find_one({
        "_id": obj_id
    })

    if not invoice:

        return {
            "msg": "No invoice found"
        }

    filename = f"invoice_{invoice_id}.pdf"

    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        rightMargin=40,
        leftMargin=40,

        topMargin=120,
        bottomMargin=40

    )

    styles = getSampleStyleSheet()

    elements = []

    # ==========================================
    # TITLE
    # ==========================================
    title = Paragraph(
        "<font size='20'><b>HDC Invoice</b></font>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # INFO
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
        ],

        [
            "Invoice No",
            invoice.get(
                "invoice_no",
                "-"
            )
        ],

        [
            "Category",
            invoice.get(
                "category",
                "-"
            )
        ]

    ]

    info_table = Table(
        info_data,
        colWidths=[180, 300]
    )

    info_table.setStyle(TableStyle([

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.black
        ),

        (
            "BACKGROUND",
            (0,0),
            (0,-1),
            colors.HexColor("#dbeafe")
        ),

        (
            "FONTNAME",
            (0,0),
            (0,-1),
            "Helvetica-Bold"
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
        "Amount"

    ]]

    rows = invoice.get(
        "rows",
        []
    )

    for row in rows:

        qty = float(
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

            str(rate),

            str(amount)

        ])

    billing_table = Table(

        table_data,

        colWidths=[
            170,
            120,
            50,
            70,
            90
        ]

    )

    billing_table.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,0),
            colors.HexColor("#2563eb")
        ),

        (
            "TEXTCOLOR",
            (0,0),
            (-1,0),
            colors.white
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
        )

    ]))

    elements.append(billing_table)

    elements.append(
        Spacer(1, 30)
    )

    # ==========================================
    # SUMMARY
    # ==========================================
    total = float(
        invoice.get("amount", 0)
    )

    discount = float(
        invoice.get("discount", 0)
    )

    paid = float(
        invoice.get("paid", 0)
    )

    balance = (
        total -
        discount -
        paid
    )

    summary_data = [

        [
            "Total",
            str(total)
        ],

        [
            "Discount",
            str(discount)
        ],

        [
            "Paid",
            str(paid)
        ],

        [
            "Balance",
            str(balance)
        ]

    ]

    summary_table = Table(
        summary_data,
        colWidths=[250, 250]
    )

    summary_table.setStyle(TableStyle([

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.black
        ),

        (
            "BACKGROUND",
            (0,0),
            (0,-1),
            colors.HexColor("#eff6ff")
        )

    ]))

    elements.append(summary_table)

    # ==========================================
    # BUILD PDF
    # ==========================================
    doc.build(elements)

    return FileResponse(

        filename,

        media_type="application/pdf",

        filename=filename

    )