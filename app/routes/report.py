from fastapi import APIRouter
from fastapi.responses import FileResponse
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

# ===== PATH FIX (IMPORTANT FOR RENDER) =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


@router.get("/{id}")
def generate_report(id: str):

    if not ObjectId.is_valid(id):
        return {"error": "Invalid ID"}

    patient = patients.find_one({"_id": ObjectId(id)})
    if not patient:
        return {"error": "Patient not found"}

    patient_checkups = list(checkups.find({"patient_id": id}))
    patient_visits = list(visits.find({"patient_id": id}))

    tasks = []
    chief = ""

    for c in patient_checkups:
        tasks.extend(c.get("tasks", []))
        chief = c.get("complaint", "")

    tooth_path = os.path.join(STATIC_DIR, "teeth.png")

    template = env.get_template("report.html")

    html_content = template.render(
        date=datetime.now().strftime("%d-%b-%Y"),
        time=datetime.now().strftime("%I:%M %p"),
        patient=patient,
        checkup_tasks=tasks,
        chief_complaint=chief,
        visits=patient_visits,
        tooth_image=tooth_path
    )

    file_path = os.path.join(UPLOAD_DIR, f"report_{id}.pdf")

    HTML(string=html_content, base_url=BASE_DIR).write_pdf(file_path)

    return FileResponse(file_path, media_type="application/pdf")