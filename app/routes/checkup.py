from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

checkups = db["checkups"]

# CREATE
@router.post("/checkups")
def create_checkup(data: dict):
    try:
        result = checkups.insert_one(data)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        return {"error": str(e)}

# GET
@router.get("/checkups")
def get_checkups():
    try:
        data = []
        for c in checkups.find():
            c["_id"] = str(c["_id"])
            data.append(c)
        return data
    except Exception as e:
        return {"error": str(e)}

# UPDATE
@router.put("/checkups/{id}")
def update_checkup(id: str, data: dict):
    try:
        checkups.update_one({"_id": ObjectId(id)}, {"$set": data})
        return {"msg": "updated"}
    except Exception as e:
        return {"error": str(e)}

# DELETE
@router.delete("/checkups/{id}")
def delete_checkup(id: str):
    try:
        checkups.delete_one({"_id": ObjectId(id)})
        return {"msg": "deleted"}
    except Exception as e:
        return {"error": str(e)}