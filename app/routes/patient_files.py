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

    except:

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

    patient["_id"] = str(patient["_id"])

    # =========================
    # CHECKUPS
    # =========================
    checkup_list = list(

        checkups.find({

            "$or": [

                {"patient_id": patient_id},

                {"patient": patient_id}

            ]

        })

    )

    for c in checkup_list:

        c["_id"] = str(c["_id"])

    # =========================
    # VISITS
    # =========================
    visit_list = list(

        visits.find({

            "$or": [

                {"patient_id": patient_id},

                {"patient": patient_id}

            ]

        })

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

        })

    )

    for i in invoice_list:

        i["_id"] = str(i["_id"])

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

        "timeline": timeline_list
    }