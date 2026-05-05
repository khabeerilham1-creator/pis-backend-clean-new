from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.database import db
from bson import ObjectId
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
visits = db["visits"]
invoices = db["invoices"]


# =========================
# GET REPORT DATA
# =========================
@router.get("/{patient_id}")
def get_report(patient_id: str):

    try:
        patient = patients.find_one({"_id": ObjectId(patient_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient["_id"] = str(patient["_id"])

    # 🔥 HANDLE BOTH patient + patient_id
    checkup_list = list(checkups.find({
        "$or": [
            {"patient": patient_id},
            {"patient_id": patient_id}
        ]
    }))

    visit_list = list(visits.find({
        "$or": [
            {"patient": patient_id},
            {"patient_id": patient_id}
        ]
    }))

    # 🔥 IMPORTANT FIX (INVOICE ISSUE)
    invoice_list = list(invoices.find({
        "$or": [
            {"patient_id": patient_id},
            {"patient_name": patient.get("name")}
        ]
    }))

    # convert IDs
    for c in checkup_list:
        c["_id"] = str(c["_id"])

    for v in visit_list:
        v["_id"] = str(v["_id"])

    for i in invoice_list:
        i["_id"] = str(i["_id"])

    return {
        "patient": patient,
        "checkups": checkup_list,
        "visits": visit_list,
        "invoices": invoice_list
    }


# =========================
# PDF REPORT
# =========================
@router.get("/pdf/{patient_id}")
def report_pdf(patient_id: str):

    try:
        patient = patients.find_one({"_id": ObjectId(patient_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient["_id"] = str(patient["_id"])

    # 🔥 FIX QUERIES (CRITICAL)
    checkup_list = list(checkups.find({
        "$or": [
            {"patient": patient_id},
            {"patient_id": patient_id}
        ]
    }))

    visit_list = list(visits.find({
        "$or": [
            {"patient": patient_id},
            {"patient_id": patient_id}
        ]
    }))

    invoice_list = list(invoices.find({
        "$or": [
            {"patient_id": patient_id},
            {"patient_name": patient.get("name")}
        ]
    }))

    # 🔥 CONVERT IDs
    for c in checkup_list:
        c["_id"] = str(c["_id"])

    for v in visit_list:
        v["_id"] = str(v["_id"])

    for i in invoice_list:
        i["_id"] = str(i["_id"])

    # 🔥 LOAD TEMPLATE
    try:
        env = Environment(loader=FileSystemLoader("app/templates"))
        template = env.get_template("report.html")
    except:
        raise HTTPException(status_code=500, detail="report.html missing")

    # 🔥 TOOTH IMAGE (FIXED)
    tooth_path = os.path.abspath("app/static/teeth.png")

    html_content = template.render(
        patient=patient,
        checkups=checkup_list,
        visits=visit_list,
        invoices=invoice_list,
        date=datetime.now().strftime("%Y-%m-%d"),
        tooth_image="file:///" + tooth_path
    )

    pdf = HTML(string=html_content).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=report.pdf"}
    )