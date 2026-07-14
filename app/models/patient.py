from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Patient(BaseModel):
    entrySheetType: str = "routine"
    shiftId: str = ""
    shiftName: str = ""
    dentistId: str = ""
    dentistName: str = ""
    doctorName: str = ""
    biography: Dict[str, Any] = Field(default_factory=dict)
    checkup: Dict[str, Any] = Field(default_factory=dict)
    plannedSequence: List[Dict[str, Any]] = Field(default_factory=list)
    implantCommencement: Dict[str, Any] = Field(default_factory=dict)
    orthodonticAssessment: Dict[str, Any] = Field(default_factory=dict)
    orthodonticAdjustments: List[Dict[str, Any]] = Field(default_factory=list)
    fullDenture: Dict[str, Any] = Field(default_factory=dict)
    invoices: List[Dict[str, Any]] = Field(default_factory=list)
    invoice: List[Dict[str, Any]] = Field(default_factory=list)
    discount: int = 0
    discountPercent: float = 0
    accountLedger: List[Dict[str, Any]] = Field(default_factory=list)
    doctorShare: List[Dict[str, Any]] = Field(default_factory=list)
    labExpenses: List[Dict[str, Any]] = Field(default_factory=list)
    labRecords: List[Dict[str, Any]] = Field(default_factory=list)
    dentalMaterials: List[Dict[str, Any]] = Field(default_factory=list)
    toothStates: Dict[str, Any] = Field(default_factory=dict)
    toothNotes: str = ""
