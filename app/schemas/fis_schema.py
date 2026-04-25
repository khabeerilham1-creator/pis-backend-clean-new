from pydantic import BaseModel
from typing import Optional


# Billing
class BillingCreate(BaseModel):
    patient_name: str
    procedure: str
    doctor: str
    amount: float
    category: Optional[str] = "general"


# Payment
class PaymentCreate(BaseModel):
    patient_name: str
    amount: float
    method: str  # cash / bank / easypaisa
    note: Optional[str] = ""


# Discount
class DiscountCreate(BaseModel):
    patient_name: str
    discount: float
    approved_by: str