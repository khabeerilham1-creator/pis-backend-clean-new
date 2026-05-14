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
# CREATE INVOICE
# ==========================================
@router.post("/")
async def create_invoice(data: dict):

    result = invoice_collection.insert_one(data)

    data["_id"] = str(result.inserted_id)

    return data

  # ==========================================
# GET ALL INVOICES
# ==========================================
@router.get("/")
async def get_invoices():

    invoices = []

    for i in invoice_collection.find():

        i["_id"] = str(i["_id"])

        invoices.append(i)

    return invoices

# ==========================================
# PDF ROUTE
# ==========================================
@router.get("/pdf/{invoice_id}")
async def generate_pdf(
    invoice_id: str
):

    try:

        invoice = invoice_collection.find_one({
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

    filename = f"invoice_{invoice_id}.pdf"

    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        topMargin=10 * mm,
        bottomMargin=10 * mm,

        leftMargin=12 * mm,
        rightMargin=12 * mm

    )

    styles = getSampleStyleSheet()

    elements = []

    # ==========================================
    # TOP SPACE
    # ==========================================
    elements.append(
        Spacer(1, 45 * mm)
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
            invoice.get(
                "mobile",
                ""
            ),

            "Category :",
            invoice.get(
                "category",
                ""
            )
        ],

        [
            "Address :",
            invoice.get(
                "address",
                ""
            ),

            "Patient Type :",
            invoice.get(
                "patient_type",
                ""
            )
        ]

    ],

    colWidths=[
        75,
        180,
        90,
        160
    ])

    bio.setStyle(TableStyle([

        ("FONTNAME",(0,0),(-1,-1),"Helvetica"),

        ("FONTSIZE",(0,0),(-1,-1),11),

        ("BOTTOMPADDING",(0,0),(-1,-1),8)

    ]))

    elements.append(bio)

    elements.append(
        Spacer(1, 10)
    )

    # ==========================================
    # TREATMENT DETAILS
    # ==========================================
    heading = Paragraph(
        "<b>Treatment Details :</b>",
        styles["Normal"]
    )

    elements.append(heading)

    elements.append(
        Spacer(1, 6)
    )

    # ==========================================
    # TOOTH IMAGE
    # ==========================================
    tooth_path = os.path.join(
        "static",
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

            row.get(
                "condition",
                ""
            ),

            row.get(
                "treatment",
                ""
            )

        ])

    treatment_table = Table(

        treatment_data,

        colWidths=[
            40,
            170,
            170,
            150
        ]

    )

    treatment_table.setStyle(TableStyle([

        ("LINEABOVE",(0,0),(-1,0),1,colors.black),
        ("LINEBELOW",(0,0),(-1,0),1,colors.black),
        ("LINEBEFORE",(0,0),(0,-1),1,colors.black),
        ("LINEAFTER",(-1,0),(-1,-1),1,colors.black),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),10),

        ("BOTTOMPADDING",(0,0),(-1,-1),8)

    ]))

    elements.append(
        treatment_table
    )

    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # INVOICE HEADING
    # ==========================================
    invoice_heading = Paragraph(
        "<b>Invoice :</b>",
        styles["Normal"]
    )

    elements.append(invoice_heading)

    elements.append(
        Spacer(1, 6)
    )

    # ==========================================
    # MERGE DUPLICATE TREATMENTS
    # ==========================================
    merged = {}

    for row in rows:

        treatment = row.get(
            "treatment",
            ""
        )

        qty = float(
            row.get(
                "qty",
                1
            )
        )

        rate = float(
            row.get(
                "rate",
                0
            )
        )

        if treatment in merged:

            merged[treatment]["qty"] += qty

        else:

            merged[treatment] = {

                "qty": qty,

                "rate": rate

            }

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

    for i, (name, data) in enumerate(
        merged.items()
    ):

        qty = data["qty"]

        rate = data["rate"]

        cost = qty * rate

        total += cost

        invoice_data.append([

            str(i + 1),

            name,

            str(int(qty)),

            str(int(rate)),

            str(int(cost))

        ])

    invoice_table = Table(

        invoice_data,

        colWidths=[
            40,
            260,
            60,
            80,
            90
        ]

    )

    invoice_table.setStyle(TableStyle([

        ("LINEABOVE",(0,0),(-1,0),1,colors.black),
        ("LINEBELOW",(0,0),(-1,0),1,colors.black),
        ("LINEBEFORE",(0,0),(0,-1),1,colors.black),
        ("LINEAFTER",(-1,0),(-1,-1),1,colors.black),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),10),

        ("BOTTOMPADDING",(0,0),(-1,-1),8)

    ]))

    elements.append(invoice_table)

    elements.append(
        Spacer(1, 15)
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
            str(int(total))
        ],

        [
            "",
            "Discount",
            str(int(discount))
        ],

        [
            "",
            "Net Amount",
            str(int(net))
        ]

    ],

    colWidths=[
        320,
        120,
        100
    ])

    totals.setStyle(TableStyle([

        ("LINEABOVE",(1,0),(-1,0),1,colors.black),
        ("LINEBELOW",(1,-1),(-1,-1),1,colors.black),
        ("LINEBEFORE",(1,0),(1,-1),1,colors.black),
        ("LINEAFTER",(-1,0),(-1,-1),1,colors.black),

        ("FONTNAME",(1,0),(-1,-1),"Helvetica-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),11),

        ("BOTTOMPADDING",(0,0),(-1,-1),8)

    ]))

    elements.append(totals)

    # ==========================================
    # BUILD PDF
    # ==========================================
    doc.build(elements)

    return FileResponse(

        filename,

        media_type="application/pdf",

        filename=filename

    )