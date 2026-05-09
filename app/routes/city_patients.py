from fastapi import APIRouter
from app.core.database import db

router = APIRouter()

patients = db["patients"]

# ==========================================
# CITY ANALYTICS
# ==========================================
@router.get("/")
async def city_patients():

    all_patients = list(
        patients.find()
    )

    city_map = {}

    for p in all_patients:

        address = str(
            p.get("address", "")
        ).lower()

        city = "Unknown"

        # ======================================
        # AUTO DETECT
        # ======================================
        if "peshawar" in address:
            city = "Peshawar"

        elif "islamabad" in address:
            city = "Islamabad"

        elif "lahore" in address:
            city = "Lahore"

        elif "karachi" in address:
            city = "Karachi"

        elif "mardan" in address:
            city = "Mardan"

        elif "swat" in address:
            city = "Swat"

        elif "charsadda" in address:
            city = "Charsadda"

        elif "kohat" in address:
            city = "Kohat"

        elif "abbottabad" in address:
            city = "Abbottabad"

        # ======================================
        # GROUP
        # ======================================
        if city not in city_map:

            city_map[city] = []

        city_map[city].append({

            "_id":
                str(p["_id"]),

            "name":
                p.get("name", ""),

            "mobile":
                p.get(
                    "mobile_number",
                    ""
                ),

            "address":
                p.get(
                    "address",
                    ""
                ),

            "reg_no":
                p.get(
                    "reg_no",
                    ""
                )
        })

    result = []

    for city, plist in city_map.items():

        result.append({

            "city":
                city,

            "count":
                len(plist),

            "patients":
                plist
        })

    return result