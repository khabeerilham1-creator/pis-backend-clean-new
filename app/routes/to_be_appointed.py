from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

appointments = db["to_be_appointed"]


# =========================
# GET ALL
# =========================
@router.get("/")
def get_all():

    data = []

    for item in appointments.find().sort(
        "created_at",
        -1
    ):

        item["_id"] = str(item["_id"])

        data.append(item)

    return data


# =========================
# CREATE
# =========================
@router.post("/")
def create(data: dict):

    item = {

        "patient_name":
        data.get("patient_name"),

        "mobile_number":
        data.get("mobile_number"),

        "address":
        data.get("address"),

        "problem":
        data.get("problem"),

        "appointment_date":
        data.get("appointment_date"),

        "status":
        data.get("status", "waiting"),

        "created_at":
        datetime.utcnow()
    }

    result = appointments.insert_one(item)

    item["_id"] = str(
        result.inserted_id
    )

    return item


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update(id: str, data: dict):

    appointments.update_one(

        {"_id": ObjectId(id)},

        {
            "$set": {

                "patient_name":
                data.get("patient_name"),

                "mobile_number":
                data.get("mobile_number"),

                "address":
                data.get("address"),

                "problem":
                data.get("problem"),

                "appointment_date":
                data.get("appointment_date"),

                "status":
                data.get("status")
            }
        }
    )

    return {
        "msg": "Updated"
    }


# =========================
# DELETE
# =========================
@router.delete("/{id}")
def delete(id: str):

    appointments.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }