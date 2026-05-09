from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

visits = db["visits"]


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

    res = visits.insert_one(data)

    new_data = visits.find_one({
        "_id": res.inserted_id
    })

    return serialize(new_data)


# =========================
# UPDATE
# =========================
@router.put("/{id}")
def update_visit(id: str, data: dict):

    visits.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )

    updated = visits.find_one({
        "_id": ObjectId(id)
    })

    return serialize(updated)


# =========================
# DELETE
# =========================
@router.delete("/{id}")
def delete_visit(id: str):

    visits.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "message": "Deleted"
    }