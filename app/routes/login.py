import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.security import create_access_token

load_dotenv()

router = APIRouter()


class LoginData(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(data: LoginData):
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_name = os.getenv("ADMIN_NAME", "HDC Admin")

    if data.username == admin_username and data.password == admin_password:
        token = create_access_token(
            {
                "sub": admin_username,
                "username": admin_username,
                "name": admin_name,
                "role": "admin",
            }
        )

        return {
            "token": token,
            "role": "admin",
            "username": admin_username,
            "name": admin_name,
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")
