from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.database import db
from bson import ObjectId

router = APIRouter()

patients = db["patients"]


@router.get("/{id}")
def generate_report(id: str):

    if not ObjectId.is_valid(id):
        return {"error": "Invalid ID"}

    patient = patients.find_one({"_id": ObjectId(id)})

    if not patient:
        return {"error": "Patient not found"}

    return HTMLResponse(f"""
        <h1>Patient Report</h1>
        <p><b>Name:</b> {patient.get('name')}</p>
        <p><b>Age:</b> {patient.get('age')}</p>
        <p><b>Gender:</b> {patient.get('gender')}</p>
        <p><b>Phone:</b> {patient.get('phone')}</p>
    """)