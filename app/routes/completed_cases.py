from fastapi import APIRouter
from app.core.database import db

router = APIRouter()

patients = db["patients"]
fis = db["fis"]

# ==========================================
# GET COMPLETED CASES
# ==========================================
@router.get("/")
async def get_completed_cases():

    data = []

    billing_records = list(
        fis.find()
    )

    for bill in billing_records:

        patient_name = bill.get(
            "patient_name",
            ""
        )

        patient = patients.find_one({
            "name": patient_name
        })

        item = {

            "_id": str(
                bill.get("_id")
            ),

            "patient_name":
                patient_name,

            "amount":
                bill.get(
                    "amount",
                    0
                ),

            "date":
                bill.get(
                    "date",
                    ""
                ),

            "lab_charge":
                bill.get(
                    "lab_charge",
                    0
                ),

            "rows":
                bill.get(
                    "rows",
                    []
                ),

            "colour_code":
                patient.get(
                    "colour_code",
                    "friends"
                ) if patient else "friends",

            "mobile_number":
                patient.get(
                    "mobile_number",
                    ""
                ) if patient else "",

            "address":
                patient.get(
                    "address",
                    ""
                ) if patient else ""
        }

        data.append(item)

    return data