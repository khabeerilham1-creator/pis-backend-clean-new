from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str
    age: int
    phone: str
    address: str
    problem: str