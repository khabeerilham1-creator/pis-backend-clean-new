from fastapi import APIRouter
from app.core.database import db
from bson import ObjectId

router = APIRouter()

checkups = db["checkups"]
afi = db["afi"]
fis = db["fis"]
cis = db["cis"]
logs = db["audit_logs"]  # 🔥 NEW


@router.get("/timeline/{patient_id}")
def get_timeline(patient_id: str):
    pid = ObjectId(patient_id)

    timeline = []

    # CHECKUPS
    for c in checkups.find({"patient_id": pid}):
        c["_id"] = str(c["_id"])
        timeline.append({
            "type": "checkup",
            "date": c.get("date"),
            "data": c
        })

    # AFI
    for a in afi.find({"patient_id": pid}):
        a["_id"] = str(a["_id"])
        timeline.append({
            "type": "afi",
            "date": a.get("date"),
            "data": a
        })

    # FIS
    for f in fis.find({"patient_id": pid}):
        f["_id"] = str(f["_id"])
        timeline.append({
            "type": "fis",
            "date": f.get("date"),
            "data": f
        })

    # CIS
    for c in cis.find({"patient_id": pid}):
        c["_id"] = str(c["_id"])
        timeline.append({
            "type": "cis",
            "date": c.get("date"),
            "data": c
        })

    # 🔥 AUDIT LOGS
    for log in logs.find({"patient_id": patient_id}):
        log["_id"] = str(log["_id"])
        timeline.append({
            "type": "log",
            "date": log.get("timestamp"),
            "data": log
        })

    # SORT
    timeline.sort(key=lambda x: x.get("date"), reverse=True)

    return timeline