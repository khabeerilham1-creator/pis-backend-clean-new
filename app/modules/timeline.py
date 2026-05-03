from datetime import datetime
from app.core.database import db

timeline = db["timeline"]

def add_to_timeline(patient_id, event_type, ref_id=None, data=None):
    timeline.insert_one({
        "patient_id": patient_id,
        "event_type": event_type,
        "ref_id": ref_id,
        "data": data or {},
        "created_at": datetime.utcnow()
    })