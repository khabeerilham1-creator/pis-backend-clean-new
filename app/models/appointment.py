from typing import Any, Dict

from pydantic import BaseModel, Field


class Appointment(BaseModel):
    date: str = ""
    time: str = ""
    clientName: str = ""
    purpose: str = ""
    mobileNumber: str = ""
    notes: str = ""
    status: str = "scheduled"
    patientId: str = ""
    registrationNo: str = ""
    shiftId: str = ""
    shiftName: str = ""
    dentistId: str = ""
    dentistName: str = ""
    doctorName: str = ""
    createdByRole: str = ""
    createdByName: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
