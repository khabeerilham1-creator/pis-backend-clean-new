from app.core.database import db
from datetime import datetime

logs = db["audit_logs"]

def log_action(user, action, patient_id=None, data=None):
    logs.insert_one({
        "user_id": user.get("id"),
        "username": user.get("username"),
        "role": user.get("role"),
        "action": action,
        "patient_id": patient_id,
        "data": data,
        "timestamp": datetime.utcnow()
    })