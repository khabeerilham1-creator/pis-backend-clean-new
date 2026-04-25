from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.core.database import db

router = APIRouter()
visits_collection = db["visits"]

class VisitCreate(BaseModel):
    patient_name: str
    diagnosis: str
    treatment: str
    teeth: list[int] = []
    medicines: str
    fee: int

@router.post("/visits")
def add_visit(data: VisitCreate):

    visits_collection.insert_one({
        "patient_name": data.patient_name,
        "diagnosis": data.diagnosis,
        "treatment": data.treatment,
        "teeth": data.teeth,
        "medicines": data.medicines,
        "fee": data.fee,
        "date": datetime.now()
    })

    return {"msg": "Visit added"}

@router.get("/visits/{patient_name}")
def get_visits(patient_name: str):

    return list(visits_collection.find(
        {"patient_name": patient_name},
        {"_id": 0}
    ))