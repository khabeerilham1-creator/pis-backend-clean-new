from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

afi = db["afi"]


# =========================
# SERIALIZER
# =========================
def serialize(item):

    item["_id"] = str(item["_id"])

    return item


# =========================
# CREATE
# =========================
@router.post("/")
def create_appointment(data: dict):

    data["created_at"] = datetime.utcnow()

    res = afi.insert_one(data)

    new_data = afi.find_one({
        "_id": res.inserted_id
    })

    return serialize(new_data)


# =========================
# GET ALL
# =========================
@router.get("/")
def get_appointments():

    data = list(

        afi.find().sort(
            "appointment_date",
            1
        )
    )

    return [
        serialize(x)
        for x in data
    ]


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update_appointment(
    id: str,
    data: dict
):

    afi.update_one(

        {
            "_id":
            ObjectId(id)
        },

        {
            "$set": data
        }
    )

    updated = afi.find_one({

        "_id":
        ObjectId(id)

    })

    return serialize(updated)


# =========================
# DELETE
# =========================
@router.delete("/{id}")
def delete_appointment(
    id: str
):

    afi.delete_one({

        "_id":
        ObjectId(id)

    })

    return {
        "msg": "Deleted"
    }