from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

excepted = db["to_be_excepted"]


# =========================
# GET ALL
# =========================
@router.get("/")
def get_all():

    data = []

    for item in excepted.find().sort(
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

        "exception_reason":
        data.get("exception_reason"),

        "status":
        data.get("status", "waiting"),

        "created_at":
        datetime.utcnow()
    }

    result = excepted.insert_one(item)

    item["_id"] = str(
        result.inserted_id
    )

    return item


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update(id: str, data: dict):

    excepted.update_one(

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

                "exception_reason":
                data.get("exception_reason"),

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

    excepted.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }