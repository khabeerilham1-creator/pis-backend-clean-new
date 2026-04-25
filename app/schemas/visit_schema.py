from pydantic import BaseModel
from typing import Optional

class VisitCreate(BaseModel):
    patient_name: str
    diagnosis: str
    medicines: str
    fee: float
    next_visit: Optional[str] = None