from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginData):

    if (
        data.username == "admin"
        and
        data.password == "admin123"
    ):

        return {
            "token": "hdc_admin_token",
            "role": "admin"
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid Credentials"
    )