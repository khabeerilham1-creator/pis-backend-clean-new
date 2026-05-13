from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.core.database import db
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

router = APIRouter()

patient_files = db["patient_files"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


# =========================
# GENERATE FULL FILE PDF
# =========================
@router.get("/patient-file-pdf/{patient_id}/{year}")
def generate_patient_file_pdf(patient_id: str, year: str):

    file = patient_files.find_one({
        "patient_id": patient_id,
        "year": year
    })

    if not file:
        return {"msg": "File not found"}

    data = file.get("data", {})

    template = env.get_template("patient_file.html")

    html = template.render(
        info=data.get("patient_info", {}),
        checkups=data.get("checkups", []),
        visits=data.get("visits", []),
        billing=data.get("invoices", []),
        payments=data.get("payments", []),
        timeline=data.get("timeline", []),
        year=year
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        f"patient_file_{patient_id}_{year}.pdf"
    )

    HTML(string=html).write_pdf(file_path)

    return FileResponse(file_path, media_type="application/pdf")