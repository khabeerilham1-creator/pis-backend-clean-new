from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Patient(BaseModel):
    biography: Dict[str, Any] = Field(default_factory=dict)
    checkup: Dict[str, Any] = Field(default_factory=dict)
    plannedSequence: List[Dict[str, Any]] = Field(default_factory=list)
    invoice: List[Dict[str, Any]] = Field(default_factory=list)
    discount: int = 0
    accountLedger: List[Dict[str, Any]] = Field(default_factory=list)
    toothStates: Dict[str, Any] = Field(default_factory=dict)
    toothNotes: str = ""
