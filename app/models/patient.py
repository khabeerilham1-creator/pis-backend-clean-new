from pydantic import BaseModel
from typing import List, Dict, Any


class Patient(BaseModel):

    biography: Dict[str, Any]

    checkup: Dict[str, Any]

    plannedSequence: List[Dict[str, Any]]

    invoice: List[Dict[str, Any]]

    discount: int = 0