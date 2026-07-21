from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.core.database import db
from app.models.appointment import Appointment

router = APIRouter(prefix="/appointments", tags=["appointments"])

SHIFT_DOCTORS = {
    "morning": {
        "shiftName": "Morning Shift",
        "doctorName": "Dr Tufyl",
        "dentistId": "dr-tufyl",
        "doctorAliases": ["Dr Tufyl"],
    },
    "evening": {
        "shiftName": "Evening Shift",
        "doctorName": "Dr Abdur Rehman",
        "dentistId": "dr-abdur-rehman",
        "doctorAliases": ["Dr Abdur Rehman"],
    },
}

VALID_STATUSES = {"scheduled", "completed", "cancelled", "missed"}


def fix_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])

    return doc


def valid_object_id(appointment_id: str) -> ObjectId:
    try:
        return ObjectId(appointment_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid appointment ID.")


def appointment_to_dict(appointment: Appointment) -> dict:
    if hasattr(appointment, "model_dump"):
        return appointment.model_dump()

    return appointment.dict()


def normalize_text(value) -> str:
    return " ".join(str(value or "").strip().lower().split())


def build_shift_query(shift: Optional[str]) -> Optional[dict]:
    shift_id = normalize_text(shift)
    details = SHIFT_DOCTORS.get(shift_id)

    if not details:
        return None

    return {
        "$or": [
            {"shiftId": shift_id},
            {"shift": shift_id},
            {"shiftName": {"$regex": details["shiftName"], "$options": "i"}},
            {"dentistId": details["dentistId"]},
            {"dentistName": {"$in": [details["doctorName"], *details.get("doctorAliases", [])]}},
            {"doctorName": {"$in": [details["doctorName"], *details.get("doctorAliases", [])]}},
        ]
    }


def clean_appointment(data: dict) -> dict:
    appointment = dict(data or {})
    appointment.pop("_id", None)

    for field in [
        "date",
        "time",
        "clientName",
        "purpose",
        "mobileNumber",
        "notes",
        "patientId",
        "registrationNo",
        "shiftId",
        "shiftName",
        "dentistId",
        "dentistName",
        "doctorName",
        "createdByRole",
        "createdByName",
    ]:
        appointment[field] = str(appointment.get(field) or "").strip()

    status = normalize_text(appointment.get("status") or "scheduled").replace(" ", "-")
    appointment["status"] = status if status in VALID_STATUSES else "scheduled"

    if not isinstance(appointment.get("metadata"), dict):
        appointment["metadata"] = {}

    if not appointment["clientName"]:
        raise HTTPException(status_code=400, detail="Client name is required.")
    if not appointment["date"]:
        raise HTTPException(status_code=400, detail="Appointment date is required.")
    if not appointment["time"]:
        raise HTTPException(status_code=400, detail="Appointment time is required.")
    if not appointment["purpose"]:
        raise HTTPException(status_code=400, detail="Purpose of visit is required.")

    return appointment


@router.get("/")
async def get_appointments(
    search: Optional[str] = Query(None),
    shift: Optional[str] = Query(None),
    dentistId: Optional[str] = Query(None),
    fromDate: Optional[str] = Query(None),
    toDate: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
    sort: str = Query("date"),
    order: int = Query(1),
):
    filters = []
    shift_query = build_shift_query(shift)

    if shift_query:
        filters.append(shift_query)

    clean_dentist_id = normalize_text(dentistId)

    if clean_dentist_id:
        filters.append(
            {
                "$or": [
                    {"dentistId": clean_dentist_id},
                    {"doctorId": clean_dentist_id},
                    {"metadata.dentistId": clean_dentist_id},
                ]
            }
        )

    date_filter = {}

    if fromDate:
        date_filter["$gte"] = str(fromDate)
    if toDate:
        date_filter["$lte"] = str(toDate)
    if date_filter:
        filters.append({"date": date_filter})

    clean_status = normalize_text(status).replace(" ", "-")

    if clean_status and clean_status != "all":
        filters.append({"status": clean_status})

    if search and search.strip():
        s = search.strip()
        filters.append(
            {
                "$or": [
                    {"clientName": {"$regex": s, "$options": "i"}},
                    {"mobileNumber": {"$regex": s, "$options": "i"}},
                    {"registrationNo": {"$regex": s, "$options": "i"}},
                    {"purpose": {"$regex": s, "$options": "i"}},
                ]
            }
        )

    if len(filters) == 1:
        query = filters[0]
    elif filters:
        query = {"$and": filters}
    else:
        query = {}

    sort_direction = 1 if int(order or 1) >= 0 else -1
    sort_field = sort if sort in {"date", "time", "clientName", "purpose", "createdAt"} else "date"
    sort_fields = [(sort_field, sort_direction)]

    if sort_field != "time":
        sort_fields.append(("time", 1))

    appointments = list(db.appointments.find(query).sort(sort_fields).limit(limit))

    return {"appointments": [fix_id(appointment) for appointment in appointments]}


@router.post("/", status_code=201)
async def create_appointment(appointment: Appointment):
    data = clean_appointment(appointment_to_dict(appointment))
    now = datetime.utcnow().isoformat()
    data["createdAt"] = now
    data["updatedAt"] = now

    try:
        result = db.appointments.insert_one(data)
    except PyMongoError as exc:
        raise HTTPException(status_code=500, detail=f"Appointment save failed. {exc}")

    data["_id"] = str(result.inserted_id)

    return {"message": "Appointment saved.", "appointment": data}


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str, appointment: Appointment):
    oid = valid_object_id(appointment_id)
    data = clean_appointment(appointment_to_dict(appointment))
    data["updatedAt"] = datetime.utcnow().isoformat()

    result = db.appointments.update_one({"_id": oid}, {"$set": data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    updated = db.appointments.find_one({"_id": oid})

    return {"message": "Appointment updated.", "appointment": fix_id(updated)}


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    oid = valid_object_id(appointment_id)
    result = db.appointments.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    return {"message": "Appointment deleted."}
