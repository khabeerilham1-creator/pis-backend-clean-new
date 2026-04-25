from fastapi import APIRouter, Request
from app.core.database import db
from bson import ObjectId

router = APIRouter()

checkups = db["checkups"]


# ================= GET ALL =================
@router.get("/checkups")
def get_checkups():
    data = []
    for c in checkups.find():
        c["_id"] = str(c["_id"])
        data.append(c)
    return data


# ================= ADD (FIXED JSON ISSUE) =================
@router.post("/checkups")
async def add_checkup(request: Request):

    data = await request.json()

    print("RECEIVED:", data)  # debug

    checkups.insert_one({
        "patient_id": data.get("patient_id"),
        "complaint": data.get("complaint"),
        "tasks": data.get("tasks", [])
    })

    return {"msg": "Saved ✅"}


# ================= UPDATE =================
@router.put("/checkups/{id}")
async def update_checkup(id: str, request: Request):

    data = await request.json()

    checkups.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "patient_id": data.get("patient_id"),
            "complaint": data.get("complaint"),
            "tasks": data.get("tasks", [])
        }}
    )

    return {"msg": "Updated ✅"}


# ================= DELETE =================
@router.delete("/checkups/{id}")
def delete_checkup(id: str):

    checkups.delete_one({"_id": ObjectId(id)})

    return {"msg": "Deleted ✅"}