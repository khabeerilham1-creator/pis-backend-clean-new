from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

patients = db["patients"]
checkups = db["checkups"]
visits = db["visits"]
invoices = db["invoices"]
timeline = db["timeline"]


# =========================
# GET PATIENT FILE
# =========================
@router.get("/{patient_id}")
def get_patient_file(patient_id: str):

    try:

        patient = patients.find_one({
            "_id": ObjectId(patient_id)
        })

    except Exception as e:

        print("PATIENT ERROR:", str(e))

        return {
            "patient": {},
            "checkups": [],
            "visits": [],
            "invoices": [],
            "timeline": []
        }

    if not patient:

        return {
            "patient": {},
            "checkups": [],
            "visits": [],
            "invoices": [],
            "timeline": []
        }

    # =========================
    # SERIALIZE PATIENT
    # =========================
    patient["_id"] = str(patient["_id"])

    # 🔥 FIX CATEGORY
    if patient.get("category") == "Category 1":
        patient["category"] = "Elite Category"

    # =========================
    # CHECKUPS
    # =========================
    checkup_list = list(

        checkups.find({

            "$or": [

                {"patient": patient_id},
                {"patient_id": patient_id},
                {"patient_name": patient.get("name")},
                {"mobile_number": patient.get("mobile_number")}

            ]

        }).sort("_id", -1)

    )

    for c in checkup_list:

        c["_id"] = str(c["_id"])

        # 🔥 FIX DUPLICATE TASKS
        unique_tasks = []
        seen = set()

        for t in c.get("tasks", []):

            key = (
                str(t.get("tooth")),
                str(t.get("condition")),
                str(t.get("treatment"))
            )

            if key not in seen:

                seen.add(key)

                unique_tasks.append(t)

        c["tasks"] = unique_tasks

    # =========================
    # VISITS
    # =========================
    visit_list = list(

        visits.find({

            "$or": [

                {"patient": patient_id},
                {"patient_id": patient_id},
                {"patient_name": patient.get("name")}

            ]

        }).sort("_id", -1)

    )

    for v in visit_list:

        v["_id"] = str(v["_id"])

    # =========================
    # INVOICES
    # =========================
    invoice_list = list(

        invoices.find({

            "$or": [

                {"patient_id": patient_id},
                {"patient_name": patient.get("name")}

            ]

        }).sort("_id", -1)

    )

    total_amount = 0
    total_paid = 0

    for i in invoice_list:

        i["_id"] = str(i["_id"])

        amount = float(i.get("amount", 0))
        paid = float(i.get("paid", 0))

        i["balance"] = amount - paid

        total_amount += amount
        total_paid += paid

        # 🔥 FIX PROCEDURES
        procedures = []

        for r in i.get("rows", []):

            treatment = r.get("treatment")

            if treatment and treatment not in procedures:
                procedures.append(treatment)

        i["procedures"] = ", ".join(procedures)

    total_balance = total_amount - total_paid

    # =========================
    # TIMELINE
    # =========================
    timeline_list = list(

        timeline.find({

            "patient_id": patient_id

        }).sort("created_at", -1)

    )

    for t in timeline_list:

        t["_id"] = str(t["_id"])

    # =========================
    # FINAL RESPONSE
    # =========================
    return {

        "patient": patient,

        "checkups": checkup_list,

        "visits": visit_list,

        "invoices": invoice_list,

        "timeline": timeline_list,

        # 🔥 SUMMARY
        "summary": {

            "total_amount": total_amount,

            "total_paid": total_paid,

            "total_balance": total_balance

        }

    }