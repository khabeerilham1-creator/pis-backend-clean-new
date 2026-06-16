from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date
from typing import Optional
from app.models.patient import Patient
from app.core.database import db

router = APIRouter(prefix="/patients", tags=["patients"])


# ── Helpers ────────────────────────────────────────────────────────────────

def fix_id(doc: dict) -> dict:
    """Convert MongoDB _id ObjectId → string so JSON can serialise it."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(pid: str) -> ObjectId:
    """Validate and return ObjectId, or raise 400."""
    try:
        return ObjectId(pid)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid patient ID format.")


# ── CREATE ─────────────────────────────────────────────────────────────────

@router.post("/", status_code=201)
async def create_patient(patient: Patient):
    """
    Save a new patient.
    Auto-generates a zero-padded Reg No (e.g. 00042).
    """
    patient_dict = patient.dict()

    # Auto Reg No — total patients + 1, padded to 5 digits
    total = db.patients.count_documents({})
    new_reg_no = str(total + 1).zfill(5)

    # Ensure biography sub-document exists
    if "biography" not in patient_dict or patient_dict["biography"] is None:
        patient_dict["biography"] = {}

    patient_dict["biography"]["regNo"] = new_reg_no

    # Timestamps
    patient_dict["createdAt"] = datetime.utcnow().isoformat()
    patient_dict["updatedAt"] = datetime.utcnow().isoformat()

    result = db.patients.insert_one(patient_dict)

    return {
        "message": "Patient saved successfully.",
        "id":      str(result.inserted_id),
        "reg_no":  new_reg_no,
    }


# ── GET ALL (with search + pagination) ────────────────────────────────────

@router.get("/")
async def get_patients(
    search: Optional[str] = Query(None, description="Search by name, phone, or reg no"),
    page:   int           = Query(1, ge=1,  description="Page number"),
    limit:  int           = Query(20, ge=1, le=100, description="Results per page"),
    sort:   str           = Query("createdAt", description="Sort field"),
    order:  int           = Query(-1, description="1=asc, -1=desc"),
):
    """
    Return all patients, with optional search and pagination.
    Search matches patient name, mobile number, or reg no.
    """
    query = {}

    if search and search.strip():
        s = search.strip()
        query["$or"] = [
            {"biography.patientName": {"$regex": s, "$options": "i"}},
            {"biography.mobileNumber": {"$regex": s, "$options": "i"}},
            {"biography.regNo":        {"$regex": s, "$options": "i"}},
        ]

    skip  = (page - 1) * limit
    total = db.patients.count_documents(query)

    patients = list(
        db.patients
        .find(query)
        .sort(sort, order)
        .skip(skip)
        .limit(limit)
    )

    for p in patients:
        fix_id(p)

    return {
        "patients":   patients,
        "total":      total,
        "page":       page,
        "totalPages": (total + limit - 1) // limit,
    }


# ── GET ONE ────────────────────────────────────────────────────────────────

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    """Return a single patient by MongoDB _id."""
    oid = valid_object_id(patient_id)
    patient = db.patients.find_one({"_id": oid})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return fix_id(patient)


# ── GET BY REG NO ──────────────────────────────────────────────────────────

@router.get("/reg/{reg_no}")
async def get_patient_by_reg(reg_no: str):
    """Find a patient by their Reg No (biography.regNo field)."""
    patient = db.patients.find_one({"biography.regNo": reg_no.zfill(5)})

    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with Reg No {reg_no} not found.")

    return fix_id(patient)


# ── UPDATE ─────────────────────────────────────────────────────────────────

@router.put("/{patient_id}")
async def update_patient(patient_id: str, patient: dict):
    """
    Full or partial update of a patient document.
    Pass only the fields you want to change.
    """
    oid = valid_object_id(patient_id)

    # Prevent overwriting _id or regNo by accident
    patient.pop("_id",    None)
    patient.pop("reg_no", None)

    # Always update timestamp
    patient["updatedAt"] = datetime.utcnow().isoformat()

    result = db.patients.update_one(
        {"_id": oid},
        {"$set": patient}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {
        "message":  "Patient updated successfully.",
        "modified": result.modified_count,
    }


# ── UPDATE TOOTH CHART ONLY ────────────────────────────────────────────────

@router.patch("/{patient_id}/tooth-chart")
async def update_tooth_chart(patient_id: str, body: dict):
    """
    Update just the toothStates and toothNotes for a patient.
    Body: { "toothStates": {"3": "crown", "11": "cavity"}, "toothNotes": "..." }
    """
    oid = valid_object_id(patient_id)

    update_fields = {
        "updatedAt": datetime.utcnow().isoformat(),
    }

    if "toothStates" in body:
        update_fields["toothStates"] = body["toothStates"]
    if "toothNotes" in body:
        update_fields["toothNotes"] = body["toothNotes"]

    result = db.patients.update_one({"_id": oid}, {"$set": update_fields})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"message": "Tooth chart updated."}


# ── DELETE ─────────────────────────────────────────────────────────────────

@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    """Permanently delete a patient record."""
    oid = valid_object_id(patient_id)

    result = db.patients.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"message": "Patient deleted successfully."}


# ── STATS ──────────────────────────────────────────────────────────────────

@router.get("/meta/stats")
async def get_stats():
    """
    Dashboard stats:
    - total patients
    - patients added today
    - total invoice revenue
    - tooth condition summary
    """
    today_str = date.today().isoformat()  # e.g. "2025-06-15"

    total_patients = db.patients.count_documents({})

    # Count patients created today (createdAt starts with today's date)
    today_patients = db.patients.count_documents({
        "createdAt": {"$regex": f"^{today_str}"}
    })

    # Sum all invoice costs across all patients
    pipeline = [
        {"$unwind": {"path": "$invoice", "preserveNullAndEmptyArrays": True}},
        {
            "$group": {
                "_id": None,
                "total": {
                    "$sum": {
                        "$convert": {
                            "input": "$invoice.cost",
                            "to": "double",
                            "onError": 0,
                            "onNull": 0,
                        }
                    }
                },
            }
        },
    ]
    revenue_result = list(db.patients.aggregate(pipeline))
    total_revenue  = revenue_result[0]["total"] if revenue_result else 0

    # Tooth condition counts across all patients
    tooth_pipeline = [
        {"$project": {"toothStates": {"$objectToArray": "$toothStates"}}},
        {"$unwind": "$toothStates"},
        {"$group": {"_id": "$toothStates.v", "count": {"$sum": 1}}},
    ]
    tooth_counts = {
        doc["_id"]: doc["count"]
        for doc in db.patients.aggregate(tooth_pipeline)
        if doc["_id"]
    }

    return {
        "totalPatients": total_patients,
        "todayPatients": today_patients,
        "totalRevenue":  round(total_revenue, 2),
        "toothConditions": tooth_counts,
    }


# ── ACCOUNT LEDGER entries ─────────────────────────────────────────────────

@router.post("/{patient_id}/ledger")
async def add_ledger_entry(patient_id: str, entry: dict):
    """
    Push a payment/ledger entry to a patient's accountLedger array.
    Entry example: { "date": "2025-06-15", "description": "Crown payment", "amount": 15000, "type": "credit" }
    """
    oid = valid_object_id(patient_id)

    entry["timestamp"] = datetime.utcnow().isoformat()

    result = db.patients.update_one(
        {"_id": oid},
        {
            "$push": {"accountLedger": entry},
            "$set":  {"updatedAt": datetime.utcnow().isoformat()},
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"message": "Ledger entry added."}
