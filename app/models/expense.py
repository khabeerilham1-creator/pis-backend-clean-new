from pydantic import BaseModel


class Expense(BaseModel):
    category: str = "clinical"
    expenseName: str = ""
    date: str = ""
    status: str = "paid"
    amount: float = 0
    details: str = ""
