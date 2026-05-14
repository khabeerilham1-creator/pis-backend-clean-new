from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.core.database import db
from bson import ObjectId

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph,
    Image
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

import os

router = APIRouter()

invoices = db["invoices"]

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# =========================================
# PDF
# =========================================
@router.get("/pdf/{invoice_id}")
async def invoice_pdf(invoice_id: str):

    try:

        invoice = invoices.find_one({
            "_id": ObjectId(invoice_id)
        })

    except:

        return {
            "msg": "Invalid invoice id"
        }

    if not invoice:

        return {
            "msg": "No invoice found"
        }

    rows = invoice.get("rows", [])

    pdf_path = os.path.join(
        BASE_DIR,
        f"invoice_{invoice_id}.pdf"
    )

    doc = SimpleDocTemplate(

        pdf_path,

        pagesize=A4,

        topMargin=10 * mm,
        bottomMargin=10 * mm,

        leftMargin=10 * mm,
        rightMargin=10 * mm

    )

    styles = getSampleStyleSheet()

    elements = []

    # =========================================
    # TITLE
    # =========================================
    title = Paragraph(

        "<b><font size='18'>HDC Invoice</font></b>",

        styles["Title"]

    )

    elements.append(title)

    elements.append(
        Spacer(1, 12)
    )

    # =========================================
    # BIO DATA
    # =========================================
    bio_data = [

        [
            "Pt. Name :",
            invoice.get(
                "patient_name",
                ""
            ),

            "Date :",
            invoice.get(
                "invoice_date",
                ""
            )
        ],

        [
            "Contact :",
            "",

            "Category:",
            invoice.get(
                "category",
                "Category 1"
            )
        ],

        [
            "Address :",
            "",

            "Patient type:",
            ""
        ]

    ]

    bio = Table(

        bio_data,

        colWidths=[
            90,
            180,
            90,
            150
        ]

    )

    bio.setStyle(TableStyle([

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
            "Helvetica"
        )

    ]))

    elements.append(bio)

    elements.append(
        Spacer(1, 15)
    )

    # =========================================
    # TOOTH IMAGE
    # =========================================
    tooth_path = os.path.join(
        BASE_DIR,
        "teeth.png"
    )

    if os.path.exists(tooth_path):

        img = Image(

            tooth_path,

            width=170 * mm,

            height=40 * mm

        )

        elements.append(img)

    elements.append(
        Spacer(1, 10)
    )

    # =========================================
    # TREATMENT DETAILS
    # =========================================
    treatment_table = [[

        "S No",
        "Details",
        "Pre Existing Condition",
        "Recommended Treatment"

    ]]

    for i, row in enumerate(rows):

        treatment_table.append([

            str(i + 1),

            row.get(
                "treatment",
                ""
            ),

            "",

            row.get(
                "treatment",
                ""
            )

        ])

    while len(treatment_table) < 7:

        treatment_table.append([
            "",
            "",
            "",
            ""
        ])

    t_table = Table(

        treatment_table,

        colWidths=[
            40,
            180,
            150,
            150
        ]

    )

    t_table.setStyle(TableStyle([

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
            (-1,0),
            colors.lightgrey
        ),

        (
            "FONTNAME",
            (0,0),
            (-1,0),
            "Helvetica-Bold"
        )

    ]))

    elements.append(
        Paragraph(
            "<b>Treatment Details :</b>",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 5)
    )

    elements.append(t_table)

    elements.append(
        Spacer(1, 20)
    )

    # =========================================
    # INVOICE TABLE
    # =========================================
    invoice_table = [[

        "S No",
        "Details",
        "Qty",
        "Rate",
        "Cost"

    ]]

    total = 0

    for i, row in enumerate(rows):

        qty = float(
            row.get("qty", 1)
        )

        rate = float(
            row.get("rate", 0)
        )

        cost = qty * rate

        total += cost

        invoice_table.append([

            str(i + 1),

            row.get(
                "treatment",
                ""
            ),

            str(qty),

            str(rate),

            str(cost)

        ])

    while len(invoice_table) < 5:

        invoice_table.append([
            "",
            "",
            "",
            "",
            ""
        ])

    inv_table = Table(

        invoice_table,

        colWidths=[
            40,
            240,
            60,
            70,
            90
        ]

    )

    inv_table.setStyle(TableStyle([

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
            (-1,0),
            colors.lightgrey
        ),

        (
            "FONTNAME",
            (0,0),
            (-1,0),
            "Helvetica-Bold"
        )

    ]))

    elements.append(
        Paragraph(
            "<b>Invoice :</b>",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 5)
    )

    elements.append(inv_table)

    elements.append(
        Spacer(1, 15)
    )

    # =========================================
    # TOTALS
    # =========================================
    discount = float(
        invoice.get(
            "discount",
            0
        )
    )

    net = total - discount

    totals = Table([

        [
            "",
            "Total Amount",
            str(total)
        ],

        [
            "",
            "Discount",
            str(discount)
        ],

        [
            "",
            "Net Amount",
            str(net)
        ]

    ],

    colWidths=[
        290,
        120,
        90
    ])

    totals.setStyle(TableStyle([

        (
            "GRID",
            (1,0),
            (-1,-1),
            1,
            colors.black
        ),

        (
            "BACKGROUND",
            (1,2),
            (-1,2),
            colors.lightgrey
        ),

        (
            "FONTNAME",
            (1,0),
            (-1,-1),
            "Helvetica-Bold"
        )

    ]))

    elements.append(totals)

    # =========================================
    # BUILD PDF
    # =========================================
    doc.build(elements)

    return FileResponse(

        pdf_path,

        media_type="application/pdf",

        filename=f"invoice_{invoice_id}.pdf"

    )