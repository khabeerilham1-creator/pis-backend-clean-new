from fastapi import APIRouter

router = APIRouter()


@router.post("/suggest")
def ai_suggest(data: dict):

    diagnosis = (data.get("diagnosis") or "").lower()
    complaints = (data.get("complaints") or "").lower()

    suggestions = []
    medicines = []
    investigations = []
    red_flags = []

    # =========================
    # TOOTH PAIN / CARIES
    # =========================
    if "pain" in diagnosis or "pain" in complaints:
        suggestions.append("Possible dental caries or pulpitis")

        investigations.append("Dental X-ray (IOPA)")

        medicines.extend([
            "Ibuprofen 400mg",
            "Paracetamol 500mg"
        ])

    # =========================
    # SWELLING / ABSCESS
    # =========================
    if "swelling" in complaints:
        suggestions.append("Possible dental abscess")

        medicines.extend([
            "Amoxicillin 500mg",
            "Metronidazole 400mg"
        ])

        investigations.append("X-ray for infection spread")

        red_flags.append("Check for fever / spreading infection")

    # =========================
    # BLEEDING GUMS
    # =========================
    if "bleeding" in complaints:
        suggestions.append("Possible gingivitis / periodontitis")

        medicines.append("Chlorhexidine mouthwash")

        investigations.append("Periodontal examination")

    # =========================
    # SENSITIVITY
    # =========================
    if "sensitivity" in complaints:
        suggestions.append("Dentin hypersensitivity")

        medicines.append("Desensitizing toothpaste")

    # =========================
    # TRAUMA / FRACTURE
    # =========================
    if "trauma" in complaints or "fracture" in diagnosis:
        suggestions.append("Possible tooth fracture")

        investigations.append("X-ray + vitality test")

        red_flags.append("Immediate dental intervention required")

    # =========================
    # DEFAULT (NO MATCH)
    # =========================
    if not suggestions:
        suggestions.append("General dental evaluation required")
        investigations.append("Basic oral examination")

    return {
        "diagnosis_suggestions": suggestions,
        "medications": list(set(medicines)),
        "investigations": list(set(investigations)),
        "red_flags": red_flags
    }