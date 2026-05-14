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

invoice_collection = db["invoices"]

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ==========================================
# PDF ROUTE
# ==========================================
@router.get("/pdf/{invoice_id}")
async def generate_pdf(
    invoice_id: str
):

    invoice = invoice_collection.find_one({
        "_id": ObjectId(invoice_id)
    })

    if not invoice:

        return {
            "msg": "No invoice found"
        }

    filename = f"invoice_{invoice_id}.pdf"

    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        topMargin=15 * mm,
        bottomMargin=15 * mm,

        leftMargin=12 * mm,
        rightMargin=12 * mm

    )

    styles = getSampleStyleSheet()

    elements = []

    # ==========================================
    # TITLE
    # ==========================================
    title = Paragraph(

        "<font size='18'><b>HDC Invoice</b></font>",

        styles["Title"]

    )

    elements.append(title)

    elements.append(
        Spacer(1, 10)
    )

    # ==========================================
    # BIO DATA
    # ==========================================
    bio = Table([

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
            "Category :",
            invoice.get(
                "category",
                ""
            )
        ],

        [
            "Address :",
            "",
            "Patient type :",
            ""
        ]

    ],

    colWidths=[
        80,
        180,
        90,
        160
    ])

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

    # ==========================================
    # TOOTH IMAGE
    # ==========================================
    tooth_path = os.path.join(
        BASE_DIR,
        "teeth"
    )

    if os.path.exists(tooth_path):

        img = Image(
            tooth_path,
            width=170 * mm,
            height=35 * mm
        )

        elements.append(img)

    elements.append(
        Spacer(1, 10)
    )

    # ==========================================
    # TREATMENT TABLE
    # ==========================================
    treatment_data = [[

        "S No",
        "Details",
        "Pre Existing Condition",
        "Recommended Treatment"

    ]]

    rows = invoice.get(
        "rows",
        []
    )

    for i, row in enumerate(rows):

        treatment_data.append([

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

    treatment_table = Table(

        treatment_data,

        colWidths=[
            40,
            180,
            150,
            150
        ]

    )

    treatment_table.setStyle(TableStyle([

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
        treatment_table
    )

    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # INVOICE TABLE
    # ==========================================
    invoice_data = [[

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

        invoice_data.append([

            str(i + 1),

            row.get(
                "treatment",
                ""
            ),

            str(qty),

            str(rate),

            str(cost)

        ])

    invoice_table = Table(

        invoice_data,

        colWidths=[
            40,
            250,
            60,
            80,
            90
        ]

    )

    invoice_table.setStyle(TableStyle([

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

    elements.append(invoice_table)

    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # TOTALS
    # ==========================================
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
        300,
        120,
        100
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

    # ==========================================
    # BUILD
    # ==========================================
    doc.build(elements)

    return FileResponse(

        filename,

        media_type="application/pdf",

        filename=filename

    )