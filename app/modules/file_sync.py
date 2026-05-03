from app.core.database import db
from datetime import datetime

patient_files = db["patient_files"]
patients = db["patients"]
checkups = db["checkups"]
visits = db["visits"]
billing = db["billing"]
payments = db["payments"]
timeline = db["timeline"]


def sync_patient_file(patient_id: str = None, phone: str = None):

    # 🔥 STEP 1: FIND PATIENT
    patient = None

    if patient_id:
        patient = patients.find_one({"_id": patient_id})

    # 🔥 fallback using phone
    if not patient and phone:
        patient = patients.find_one({"phone": phone})

    if not patient:
        print("❌ Patient not found for file sync")
        return

    patient_id = str(patient["_id"])
    year = str(datetime.utcnow().year)

    # 🔥 STEP 2: BUILD DATA
    data = {
        "patient_info": patient,
        "checkups": list(checkups.find({"patient_id": patient_id}, {"_id": 0})),
        "visits": list(visits.find({"patient_id": patient_id}, {"_id": 0})),
        "billing": list(billing.find({"patient_id": patient_id}, {"_id": 0})),
        "payments": list(payments.find({"patient_id": patient_id}, {"_id": 0})),
        "timeline": list(timeline.find({"patient_id": patient_id}, {"_id": 0}))
    }

    data["patient_info"].pop("_id", None)

    # 🔥 STEP 3: SAVE FILE
    patient_files.update_one(
        {"patient_id": patient_id, "year": year},
        {
            "$set": {
                "patient_id": patient_id,
                "phone": patient.get("phone"),  # ✅ IMPORTANT
                "name": patient.get("name"),    # ✅ IMPORTANT
                "year": year,
                "data": data,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    print("✅ Patient file synced")