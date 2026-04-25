from fastapi import APIRouter, UploadFile, File, Form
from app.core.database import db
from datetime import datetime
import os

router = APIRouter()
cis = db["cis"]

@router.post("/cis")
async def create(
    patient_id: int = Form(...),
    treatment_plan: str = Form(""),
    photo: UploadFile = File(None)
):

    path = ""

    if photo:
        os.makedirs("uploads", exist_ok=True)
        path = f"uploads/{photo.filename}"
        with open(path, "wb") as f:
            f.write(await photo.read())

    cis.insert_one({
        "patient": patient_id,
        "treatment_plan": treatment_plan,
        "photo": path,
        "created_at": datetime.now()
    })

    return {"msg": "Saved"}