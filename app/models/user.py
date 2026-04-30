from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "staff"  # admin / doctor / staff


class UserLogin(BaseModel):
    username: str
    password: str