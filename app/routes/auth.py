from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginData):

    # LOGIN CREDENTIALS
    if (
        data.username == "hdc1122"
        and
        data.password == "drzaffar"
    ):

        return {
            "token": "hdc_admin_token",
            "role": "admin",

            # OPTIONAL USER INFO
            "username": "hdc1122",
            "name": "HDC Admin"
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid Credentials"
    )
