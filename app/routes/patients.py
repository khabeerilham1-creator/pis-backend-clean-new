from datetime import date, datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.database import db
from app.models.patient import Patient

router = APIRouter(prefix="/patients", tags=["patients"])

SHIFT_DOCTORS = {
    "morning": {
        "shiftName": "Morning Shift",
        "doctorName": "Dr Tufyl",
    },
    "evening": {
        "shiftName": "Evening Shift",
        "doctorName": "Dr Abdur Rehman",
    },
}


def fix_id(doc: dict) -> dict:
    """Convert MongoDB _id ObjectId to string so JSON can serialise it."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def valid_object_id(pid: str) -> ObjectId:
    try:
        return ObjectId(pid)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid patient ID format.")


def patient_to_dict(patient: Patient) -> dict:
    if hasattr(patient, "model_dump"):
        return patient.model_dump()

    return patient.dict()


def iso_value(value):
    if isinstance(value, datetime):
        return value.isoformat()

    return value


def normalize_text(value) -> str:
    return " ".join(str(value or "").strip().lower().split())


def infer_shift_id(doc: dict, biography: dict) -> str:
    explicit_shift = (
        doc.get("shiftId")
        or doc.get("shift")
        or biography.get("shiftId")
        or biography.get("shift")
        or biography.get("shiftName")
    )
    clean_shift = normalize_text(explicit_shift)

    for shift_id, details in SHIFT_DOCTORS.items():
        if clean_shift in {shift_id, normalize_text(details["shiftName"])}:
            return shift_id

    doctor_name = normalize_text(biography.get("doctorName"))

    for shift_id, details in SHIFT_DOCTORS.items():
        if doctor_name == normalize_text(details["doctorName"]):
            return shift_id

    return ""


def build_shift_query(shift: Optional[str]) -> Optional[dict]:
    shift_id = normalize_text(shift)
    details = SHIFT_DOCTORS.get(shift_id)

    if not details:
        return None

    return {
        "$or": [
            {"shiftId": shift_id},
            {"shift": shift_id},
            {"biography.shiftId": shift_id},
            {"biography.shift": shift_id},
            {"shiftName": {"$regex": details["shiftName"], "$options": "i"}},
            {"biography.shiftName": {"$regex": details["shiftName"], "$options": "i"}},
            {"biography.doctorName": {"$regex": f"^{details['doctorName']}$", "$options": "i"}},
        ]
    }


def normalize_patient(doc: dict) -> dict:
    """Return old flat records and current records in the current frontend shape."""
    if not doc:
        return doc

    biography = dict(doc.get("biography") or {})
    legacy_bio_fields = {
        "regNo": ("reg_no", "registration_no"),
        "patientName": ("name", "patient_name"),
        "mobileNumber": ("mobile_number", "phone"),
        "category": ("category",),
        "patientType": ("purpose_of_visit", "patient_type"),
        "age": ("age",),
        "email": ("email",),
        "address": ("address",),
        "gender": ("gender",),
        "occupation": ("occupation",),
        "date": ("date",),
        "referredBy": ("referred_by",),
        "emergencyNumber": ("emergency_number",),
        "ptclNumber": ("ptcl_number",),
    }

    for target, legacy_keys in legacy_bio_fields.items():
        if biography.get(target):
            continue

        for legacy_key in legacy_keys:
            if doc.get(legacy_key) not in (None, ""):
                biography[target] = str(doc.get(legacy_key))
                break

    doc["biography"] = biography
    shift_id = infer_shift_id(doc, biography)

    if shift_id:
        shift_details = SHIFT_DOCTORS[shift_id]
        doc["shiftId"] = doc.get("shiftId") or shift_id
        doc["shiftName"] = doc.get("shiftName") or shift_details["shiftName"]
        biography["shiftId"] = biography.get("shiftId") or shift_id
        biography["shiftName"] = biography.get("shiftName") or shift_details["shiftName"]
        biography["doctorName"] = biography.get("doctorName") or shift_details["doctorName"]

    doc.setdefault("checkup", {})
    doc.setdefault("plannedSequence", [])
    doc.setdefault("invoice", [])
    doc.setdefault("discount", 0)
    doc.setdefault("discountPercent", 0)
    doc.setdefault("accountLedger", [])
    doc.setdefault("doctorShare", [])
    doc.setdefault("labExpenses", [])
    doc.setdefault("labRecords", [])
    doc.setdefault("dentalMaterials", [])
    doc.setdefault("toothStates", {})
    doc.setdefault("toothNotes", "")

    if not doc.get("createdAt") and doc.get("created_at"):
        doc["createdAt"] = iso_value(doc.get("created_at"))
    if not doc.get("updatedAt"):
        doc["updatedAt"] = iso_value(doc.get("updated_at") or doc.get("createdAt") or doc.get("created_at"))

    return fix_id(doc)


def next_reg_no() -> str:
    max_number = 0

    for doc in db.patients.find({}, {"biography.regNo": 1, "reg_no": 1}):
        biography = doc.get("biography") or {}
        raw_reg_no = biography.get("regNo") or doc.get("reg_no") or ""
        digits = "".join(ch for ch in str(raw_reg_no) if ch.isdigit())

        if digits:
            max_number = max(max_number, int(digits))

    return str(max_number + 1).zfill(5)


@router.post("/", status_code=201)
async def create_patient(patient: Patient):
    last_duplicate = None

    for attempt in range(5):
        try:
            patient_dict = patient_to_dict(patient)
            new_reg_no = next_reg_no()

            if attempt:
                new_reg_no = str(int(new_reg_no) + attempt).zfill(5)

            if "biography" not in patient_dict or patient_dict["biography"] is None:
                patient_dict["biography"] = {}

            patient_dict["biography"]["regNo"] = new_reg_no

            now = datetime.utcnow().isoformat()
            patient_dict["createdAt"] = now
            patient_dict["updatedAt"] = now

            result = db.patients.insert_one(patient_dict)

            return {
                "message": "Patient saved successfully.",
                "id": str(result.inserted_id),
                "reg_no": new_reg_no,
            }
        except DuplicateKeyError as exc:
            last_duplicate = exc
            continue
        except PyMongoError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Patient save failed. Check MongoDB connection and patient data. {exc}",
            )

    raise HTTPException(
        status_code=409,
        detail=f"Could not generate a unique registration number. {last_duplicate}",
    )


@router.get("/")
async def get_patients(
    search: Optional[str] = Query(None, description="Search by name, phone, or reg no"),
    shift: Optional[str] = Query(None, description="Filter by clinic shift"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    sort: str = Query("createdAt", description="Sort field"),
    order: int = Query(-1, description="1=asc, -1=desc"),
):
    filters = []

    if search and search.strip():
        s = search.strip()
        filters.append(
            {
                "$or": [
                    {"biography.patientName": {"$regex": s, "$options": "i"}},
                    {"biography.mobileNumber": {"$regex": s, "$options": "i"}},
                    {"biography.regNo": {"$regex": s, "$options": "i"}},
                    {"name": {"$regex": s, "$options": "i"}},
                    {"mobile_number": {"$regex": s, "$options": "i"}},
                    {"reg_no": {"$regex": s, "$options": "i"}},
                ]
            }
        )

    shift_query = build_shift_query(shift)

    if shift_query:
        filters.append(shift_query)

    if len(filters) == 1:
        query = filters[0]
    elif filters:
        query = {"$and": filters}
    else:
        query = {}

    skip = (page - 1) * limit
    total = db.patients.count_documents(query)
    patients = list(
        db.patients
        .find(query)
        .sort(sort, order)
        .skip(skip)
        .limit(limit)
    )

    return {
        "patients": [normalize_patient(patient) for patient in patients],
        "total": total,
        "page": page,
        "totalPages": (total + limit - 1) // limit,
    }


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    oid = valid_object_id(patient_id)
    patient = db.patients.find_one({"_id": oid})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return normalize_patient(patient)


@router.get("/reg/{reg_no}")
async def get_patient_by_reg(reg_no: str):
    padded_reg_no = reg_no.zfill(5)
    patient = db.patients.find_one(
        {
            "$or": [
                {"biography.regNo": padded_reg_no},
                {"reg_no": padded_reg_no},
            ]
        }
    )

    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with Reg No {reg_no} not found.")

    return normalize_patient(patient)


@router.put("/{patient_id}")
async def update_patient(patient_id: str, patient: dict):
    oid = valid_object_id(patient_id)

    patient.pop("_id", None)
    patient.pop("reg_no", None)
    patient["updatedAt"] = datetime.utcnow().isoformat()

    result = db.patients.update_one({"_id": oid}, {"$set": patient})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {
        "message": "Patient updated successfully.",
        "modified": result.modified_count,
    }


@router.patch("/{patient_id}/tooth-chart")
async def update_tooth_chart(patient_id: str, body: dict):
    oid = valid_object_id(patient_id)
    update_fields = {"updatedAt": datetime.utcnow().isoformat()}

    if "toothStates" in body:
        update_fields["toothStates"] = body["toothStates"]
    if "toothNotes" in body:
        update_fields["toothNotes"] = body["toothNotes"]

    result = db.patients.update_one({"_id": oid}, {"$set": update_fields})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"message": "Tooth chart updated."}


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    oid = valid_object_id(patient_id)
    result = db.patients.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"message": "Patient deleted successfully."}


@router.get("/meta/stats")
async def get_stats():
    today_str = date.today().isoformat()
    total_patients = db.patients.count_documents({})
    today_patients = db.patients.count_documents(
        {
            "$or": [
                {"createdAt": {"$regex": f"^{today_str}"}},
                {"date": today_str},
            ]
        }
    )

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
    total_revenue = revenue_result[0]["total"] if revenue_result else 0

    tooth_pipeline = [
        {"$project": {"toothStates": {"$objectToArray": {"$ifNull": ["$toothStates", {}]}}}},
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
        "totalRevenue": round(total_revenue, 2),
        "toothConditions": tooth_counts,
    }


@router.post("/{patient_id}/ledger")
async def add_ledger_entry(patient_id: str, entry: dict):
    oid = valid_object_id(patient_id)
    entry["timestamp"] = datetime.utcnow().isoformat()

    result = db.patients.update_one(
        {"_id": oid},
        {
            "$push": {"accountLedger": entry},
            "$set": {"updatedAt": datetime.utcnow().isoformat()},
        },
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"message": "Ledger entry added."}
