from pydantic import BaseModel


class InventoryItem(BaseModel):
    productName: str = ""
    qty: float = 0
    date: str = ""
    minQty: float = 5
    notes: str = ""
