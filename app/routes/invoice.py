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
# COLOR GRADING SYSTEM
# ==========================================
CATEGORY_COLORS = {
    "GREEN": "#16a34a",
    "BLUE": "#2563eb",
    "PURPLE": "#9333ea",
    "RED": "#dc2626",
    "GOLD": "#ca8a04"
}

# ==========================================
# CREATE
# ==========================================
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

# ==========================================
# GET
# ==========================================
@router.get("/")
async def get_invoices():

    data = []

    for item in invoice_collection.find():

        item["_id"] = str(item["_id"])

        data.append(item)

    return data

# ==========================================
# UPDATE
# ==========================================
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
            "msg": "No invoice"
        }

    # ==========================================
    # CATEGORY COLOR
    # ==========================================
    category = invoice.get(
        "category",
        "GREEN"
    )

    main_color = CATEGORY_COLORS.get(
        category,
        "#16a34a"
    )

    light_color = colors.HexColor(
        "#dcfce7"
    )

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

    # ==========================================
    # TITLE
    # ==========================================
    title = Table(
        [[
            Paragraph(
                "<font color='white'><b>HDC Invoice</b></font>",
                styles["Title"]
            )
        ]],
        colWidths=[500]
    )

    title.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,-1),
            colors.HexColor(main_color)
        ),

        (
            "ALIGN",
            (0,0),
            (-1,-1),
            "CENTER"
        ),

        (
            "BOX",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor(main_color)
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
    patient_info = Paragraph(
        f"<b>Patient:</b> {patient_name}",
        styles["Heading2"]
    )

    elements.append(patient_info)

    elements.append(
        Spacer(1, 15)
    )

    # ==========================================
    # BILLING HEADER
    # ==========================================
    billing_header = Table(
        [[
            Paragraph(
                f"<font color='{main_color}'><b>BILLING DETAILS</b></font>",
                styles["Heading3"]
            )
        ]],
        colWidths=[500]
    )

    billing_header.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,-1),
            light_color
        ),

        (
            "BOX",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor(main_color)
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

    elements.append(
        billing_header
    )

    # ==========================================
    # TABLE DATA
    # ==========================================
    data = [[
        "Procedure",
        "Doctor",
        "Qty",
        "Rate",
        "Amount"
    ]]

    rows = invoice.get("rows", [])

    # ==========================================
    # NEW DATA
    # ==========================================
    if rows:

        for row in rows:

            qty = int(
                row.get("qty", 1)
            )

            rate = float(
                row.get("rate", 0)
            )

            amount = qty * rate

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

                f"Rs {rate}",

                f"Rs {amount}"

            ])

    # ==========================================
    # OLD DATA SUPPORT
    # ==========================================
    else:

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

        split_amount = int(
            invoice.get(
                "amount",
                0
            ) / max(
                len(procedures),
                1
            )
        )

        for i, proc in enumerate(
            procedures
        ):

            data.append([

                proc.strip(),

                doctors[i].strip()
                if i < len(doctors)
                else "",

                "1",

                f"Rs {split_amount}",

                f"Rs {split_amount}"

            ])

    # ==========================================
    # MAIN TABLE
    # ==========================================
    table = Table(
        data,
        colWidths=[
            190,
            120,
            50,
            70,
            70
        ]
    )

    table.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,0),
            light_color
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
            colors.HexColor("#d1d5db")
        ),

        (
            "BOX",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor(main_color)
        ),

        (
            "ALIGN",
            (2,1),
            (-1,-1),
            "CENTER"
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
        )

    ]))

    elements.append(table)

    elements.append(
        Spacer(1, 25)
    )

    # ==========================================
    # SUMMARY HEADER
    # ==========================================
    summary_header = Table(
        [[
            Paragraph(
                f"<font color='{main_color}'><b>SUMMARY</b></font>",
                styles["Heading3"]
            )
        ]],
        colWidths=[500]
    )

    summary_header.setStyle(TableStyle([

        (
            "BACKGROUND",
            (0,0),
            (-1,-1),
            light_color
        ),

        (
            "BOX",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor(main_color)
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

    elements.append(
        summary_header
    )

    # ==========================================
    # SUMMARY TABLE
    # ==========================================
    summary = Table([

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

    ],
    colWidths=[250, 250])

    summary.setStyle(TableStyle([

        (
            "GRID",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor("#d1d5db")
        ),

        (
            "BOX",
            (0,0),
            (-1,-1),
            1,
            colors.HexColor(main_color)
        ),

        (
            "FONTNAME",
            (0,0),
            (-1,-1),
            "Helvetica-Bold"
        ),

        (
            "ALIGN",
            (1,0),
            (-1,-1),
            "CENTER"
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

    elements.append(summary)

    # ==========================================
    # BUILD
    # ==========================================
    doc.build(elements)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )