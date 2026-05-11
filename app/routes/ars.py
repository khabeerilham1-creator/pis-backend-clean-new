from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

alerts = db["alerts"]


# =========================
# CREATE ALERT
# =========================
@router.post("/")
def create_alert(data: dict):

    alert = {

        "patient_name":
        data.get("patient_name"),

        "type":
        data.get("type"),

        "message":
        data.get("message"),

        "priority":
        data.get(
            "priority",
            "medium"
        ),

        "date":
        data.get("date"),

        "status":
        "pending",

        "created_at":
        datetime.utcnow()
    }

    alerts.insert_one(alert)

    return {
        "msg": "Alert Created"
    }


# =========================
# GET ALERTS
# =========================
@router.get("/")
def get_alerts():

    data = []

    for a in alerts.find().sort(
        "created_at",
        -1
    ):

        a["_id"] = str(a["_id"])

        data.append(a)

    return data


# =========================
# COMPLETE ALERT
# =========================
@router.put("/{id}")
def complete_alert(id: str):

    alerts.update_one(

        {
            "_id": ObjectId(id)
        },

        {
            "$set": {
                "status": "done"
            }
        }
    )

    return {
        "msg": "Completed"
    }


# =========================
# DELETE ALERT
# =========================
@router.delete("/{id}")
def delete_alert(id: str):

    alerts.delete_one({

        "_id": ObjectId(id)
    })

    return {
        "msg": "Deleted"
    }