from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

visits = db["visits"]
afi = db["afi"]


# =========================
# SERIALIZER
# =========================
def serialize(v):

    v["_id"] = str(v["_id"])

    return v


# =========================
# GET ALL
# =========================
@router.get("/")
def get_visits():

    data = list(
        visits.find().sort("_id", -1)
    )

    return [serialize(v) for v in data]


# =========================
# CREATE
# =========================
@router.post("/")
def create_visit(data: dict):

    # SAVE VISIT
    res = visits.insert_one(data)

    new_data = visits.find_one({
        "_id": res.inserted_id
    })

    # =========================
    # AUTO CREATE APPOINTMENT
    # =========================
    patient_name = (
        data.get("patient_name")
        or data.get("name")
        or data.get("patient")
        or ""
    )

    visit_date = (
        data.get("date")
        or data.get("visit_date")
        or ""
    )

    doctor = data.get(
        "doctor",
        ""
    )

    treatment = data.get(
        "treatment",
        ""
    )

    if patient_name and visit_date:

        existing = afi.find_one({

            "patient_name":
            patient_name,

            "date":
            visit_date,

            "treatment":
            treatment
        })

        if not existing:

            afi.insert_one({

                "patient_name":
                patient_name,

                "date":
                visit_date,

                "doctor":
                doctor,

                "treatment":
                treatment,

                "status":
                "Auto Added",

                "source":
                "Planned Sequence Of Treatment",

                "created_at":
                datetime.utcnow()
            })

            print(
                "✅ AUTO APPOINTMENT CREATED"
            )

    return serialize(new_data)


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update_visit(id: str, data: dict):

    visits.update_one(

        {
            "_id": ObjectId(id)
        },

        {
            "$set": data
        }
    )

    updated = visits.find_one({

        "_id": ObjectId(id)
    })

    # =========================
    # UPDATE APPOINTMENT
    # =========================
    patient_name = (
        data.get("patient_name")
        or data.get("name")
        or data.get("patient")
        or ""
    )

    visit_date = (
        data.get("date")
        or data.get("visit_date")
        or ""
    )

    doctor = data.get(
        "doctor",
        ""
    )

    treatment = data.get(
        "treatment",
        ""
    )

    if patient_name and visit_date:

        existing = afi.find_one({

            "patient_name":
            patient_name,

            "treatment":
            treatment
        })

        if existing:

            afi.update_one(

                {
                    "_id":
                    existing["_id"]
                },

                {
                    "$set": {

                        "date":
                        visit_date,

                        "doctor":
                        doctor,

                        "treatment":
                        treatment
                    }
                }
            )

        else:

            afi.insert_one({

                "patient_name":
                patient_name,

                "date":
                visit_date,

                "doctor":
                doctor,

                "treatment":
                treatment,

                "status":
                "Auto Added",

                "source":
                "Planned Sequence Of Treatment",

                "created_at":
                datetime.utcnow()
            })

    return serialize(updated)


# =========================
# DELETE
# =========================
@router.delete("/{id}")
def delete_visit(id: str):

    visit = visits.find_one({

        "_id": ObjectId(id)
    })

    if visit:

        patient_name = (
            visit.get("patient_name")
            or visit.get("name")
            or visit.get("patient")
            or ""
        )

        treatment = visit.get(
            "treatment",
            ""
        )

        # DELETE AUTO APPOINTMENT
        afi.delete_many({

            "patient_name":
            patient_name,

            "treatment":
            treatment,

            "source":
            "Planned Sequence Of Treatment"
        })

    visits.delete_one({

        "_id": ObjectId(id)
    })

    return {

        "message":
        "Deleted"
    }