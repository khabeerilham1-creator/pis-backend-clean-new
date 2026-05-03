from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.core.database import db
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import re

router = APIRouter()

prescriptions = db["prescriptions"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


# =========================
# CREATE
# =========================
@router.post("/")
def create_prescription(data: dict):
    data["created_at"] = datetime.utcnow()
    prescriptions.insert_one(data)
    return {"msg": "Saved"}


# =========================
# PDF GENERATE
# =========================
@router.get("/pdf/{name}")
def generate_pdf(name: str):

    print("SEARCH NAME:", name)  # debug

    # ✅ FIXED SEARCH (case insensitive)
    data = prescriptions.find_one({
        "name": {"$regex": f"^{name}$", "$options": "i"}
    })

    if not data:
        return {"msg": "Not found"}

    template = env.get_template("prescription.html")

    html = template.render(
        patient=data,
        date=data.get("date"),
        medicines=data.get("medicines", []),
        notes=data.get("notes", "")
    )

    file_path = os.path.join(UPLOAD_DIR, f"prescription_{name}.pdf")

    HTML(string=html).write_pdf(file_path)

    return FileResponse(file_path, media_type="application/pdf")