from fastapi import APIRouter, HTTPException
from app.core.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

patients = db["patients"]


# =========================
# GET ALL
# =========================
@router.get("/")
def get_patients():

    data = []

    for p in patients.find().sort("created_at", -1):

        p["_id"] = str(p["_id"])

        data.append(p)

    return data


# =========================
# GET MONTHS
# =========================
@router.get("/months")
def get_months():

    months = patients.aggregate([

        {
            "$group": {

                "_id": {

                    "year": "$year",
                    "month": "$month",
                    "month_no": "$month_no"
                },

                "count": {
                    "$sum": 1
                }
            }
        },

        {
            "$sort": {

                "_id.year": -1,
                "_id.month_no": -1
            }
        }
    ])

    result = []

    for m in months:

        result.append({

            "year":
            m["_id"]["year"],

            "month":
            m["_id"]["month"],

            "month_no":
            m["_id"]["month_no"],

            "count":
            m["count"]
        })

    return result


# =========================
# GET PATIENTS BY MONTH
# =========================
@router.get("/month/{year}/{month}")
def get_month_patients(
    year: int,
    month: int
):

    data = list(

        patients.find({

            "year": year,
            "month_no": month

        }).sort("created_at", -1)
    )

    result = []

    for p in data:

        p["_id"] = str(p["_id"])

        result.append(p)

    return result


# =========================
# CREATE
# =========================
@router.post("/")
async def create_patient(data: dict):

    try:

        # 🔥 IMPORTANT FIX
        if data.get("date"):

            now = datetime.strptime(
                data.get("date"),
                "%Y-%m-%d"
            )

        else:

            now = datetime.utcnow()

        patient = {

            "reg_no":
            data.get("reg_no", ""),

            "date":
            data.get("date", ""),

            "title":
            data.get("title", "Mr."),

            "name":
            data.get("name", ""),

            "birth_date":
            data.get("birth_date", ""),

            "age":
            data.get("age", ""),

            "gender":
            data.get("gender", ""),

            "occupation":
            data.get("occupation", ""),

            "address":
            data.get("address", ""),

            "email":
            data.get("email", ""),

            "ptcl_number":
            data.get("ptcl_number", ""),

            "mobile_number":
            data.get("mobile_number", ""),

            "emergency_number":
            data.get(
                "emergency_number",
                ""
            ),

            "referred_by":
            data.get(
                "referred_by",
                ""
            ),

            "category":
            data.get("category", ""),

            "colour_code":
            data.get(
                "colour_code",
                "green"
            ),

            "purpose_of_visit":
            data.get(
                "purpose_of_visit",
                ""
            ),

            "consultation_fee_paid":
            data.get(
                "consultation_fee_paid",
                "No"
            ),

            "conditions":
            data.get(
                "conditions",
                ""
            ),

            "complaints":
            data.get(
                "complaints",
                "segmental"
            ),

            # =========================
            # DATE SYSTEM
            # =========================
            "created_at":
            datetime.utcnow(),

            "year":
            now.year,

            "month":
            now.strftime("%B"),

            "month_no":
            now.month,

            "day":
            now.day
        }

        result = patients.insert_one(
            patient
        )

        patient["_id"] = str(
            result.inserted_id
        )

        return patient

    except Exception as e:

        print(
            "CREATE ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =========================
# UPDATE
# =========================
@router.put("/{id}")
async def update_patient(
    id: str,
    data: dict
):

    try:

        if data.get("date"):

            now = datetime.strptime(
                data.get("date"),
                "%Y-%m-%d"
            )

        else:

            now = datetime.utcnow()

        patients.update_one(

            {
                "_id":
                ObjectId(id)
            },

            {
                "$set": {

                    "reg_no":
                    data.get(
                        "reg_no",
                        ""
                    ),

                    "date":
                    data.get(
                        "date",
                        ""
                    ),

                    "title":
                    data.get(
                        "title",
                        "Mr."
                    ),

                    "name":
                    data.get(
                        "name",
                        ""
                    ),

                    "birth_date":
                    data.get(
                        "birth_date",
                        ""
                    ),

                    "age":
                    data.get(
                        "age",
                        ""
                    ),

                    "gender":
                    data.get(
                        "gender",
                        ""
                    ),

                    "occupation":
                    data.get(
                        "occupation",
                        ""
                    ),

                    "address":
                    data.get(
                        "address",
                        ""
                    ),

                    "email":
                    data.get(
                        "email",
                        ""
                    ),

                    "ptcl_number":
                    data.get(
                        "ptcl_number",
                        ""
                    ),

                    "mobile_number":
                    data.get(
                        "mobile_number",
                        ""
                    ),

                    "emergency_number":
                    data.get(
                        "emergency_number",
                        ""
                    ),

                    "referred_by":
                    data.get(
                        "referred_by",
                        ""
                    ),

                    "category":
                    data.get(
                        "category",
                        ""
                    ),

                    "colour_code":
                    data.get(
                        "colour_code",
                        "green"
                    ),

                    "purpose_of_visit":
                    data.get(
                        "purpose_of_visit",
                        ""
                    ),

                    "consultation_fee_paid":
                    data.get(
                        "consultation_fee_paid",
                        "No"
                    ),

                    "conditions":
                    data.get(
                        "conditions",
                        ""
                    ),

                    "complaints":
                    data.get(
                        "complaints",
                        "segmental"
                    ),

                    # 🔥 UPDATE MONTH DATA TOO
                    "year":
                    now.year,

                    "month":
                    now.strftime("%B"),

                    "month_no":
                    now.month,

                    "day":
                    now.day
                }
            }
        )

        updated = patients.find_one({

            "_id":
            ObjectId(id)

        })

        if updated:

            updated["_id"] = str(
                updated["_id"]
            )

        return updated

    except Exception as e:

        print(
            "UPDATE ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =========================
# DELETE
# =========================
@router.delete("/{id}")
async def delete_patient(
    id: str
):

    try:

        patients.delete_one({

            "_id":
            ObjectId(id)

        })

        return {

            "msg":
            "Deleted ✅"
        }

    except Exception as e:

        print(
            "DELETE ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =========================
# SINGLE
# =========================
@router.get("/{id}")
def get_single_patient(
    id: str
):

    try:

        patient = patients.find_one({

            "_id":
            ObjectId(id)

        })

        if not patient:

            raise HTTPException(

                status_code=404,

                detail="Patient not found"
            )

        patient["_id"] = str(
            patient["_id"]
        )

        return patient

    except Exception as e:

        print(
            "GET ERROR:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )